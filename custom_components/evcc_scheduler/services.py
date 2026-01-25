import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_services(hass: HomeAssistant):
    """Registriere Services für Plan-Verwaltung"""

    def _get_coordinator():
        """Hole den aktiven Coordinator oder werfe eine saubere ValidationError."""
        domain_data = hass.data.get(DOMAIN)
        if not domain_data:
            raise ServiceValidationError("Integration nicht initialisiert; bitte erneut laden.")

        coordinator = next(iter(domain_data.values()), None)
        if not coordinator:
            raise ServiceValidationError("Kein aktiver Coordinator gefunden; bitte Integration neu laden.")

        return coordinator

    async def _get_vehicles(coordinator) -> dict:
        """Hole Fahrzeuge-Daten aus EVCC-State (ein API-Call)."""
        evcc_state = await coordinator.api.get_state()
        return evcc_state.get("vehicles", {})

    def _ensure_vehicle_exists(all_vehicles: dict, vehicle_id: str) -> None:
        """Validiere, dass das Fahrzeug existiert, sonst ServiceValidationError werfen."""
        if vehicle_id not in all_vehicles:
            available_vehicles = ", ".join(all_vehicles.keys()) if all_vehicles else "keine"
            raise ServiceValidationError(
                f"Das Fahrzeug '{vehicle_id}' ist in EVCC nicht angelegt. "
                f"Verfügbare Fahrzeuge: {available_vehicles}"
            )

    def _parse_plan_index(raw_index, plans_len: int | None = None) -> int:
        """Wandle 1-basierten Index in 0-basiert um und prüfe Reichweite."""
        try:
            idx_1_based = int(raw_index)
        except (TypeError, ValueError):
            raise ServiceValidationError("Plan-Index muss eine Ganzzahl sein") from None

        if idx_1_based < 1:
            raise ServiceValidationError("Plan-Index muss >= 1 sein")

        if plans_len is not None and idx_1_based > plans_len:
            raise ServiceValidationError(f"Plan-Index {idx_1_based} ungültig")

        return idx_1_based - 1

    def _validate_time(value: str) -> str:
        if not isinstance(value, str):
            raise ServiceValidationError("'time' muss ein String im Format HH:MM sein")
        parts = value.split(":")
        if len(parts) != 2:
            raise ServiceValidationError("'time' muss im Format HH:MM vorliegen")
        try:
            hour = int(parts[0])
            minute = int(parts[1])
        except ValueError:
            raise ServiceValidationError("'time' muss Zahlen im Format HH:MM enthalten") from None
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ServiceValidationError("'time' muss eine gültige Uhrzeit (00:00-23:59) sein")
        return f"{hour:02d}:{minute:02d}"

    def _validate_weekdays(value) -> list[int]:
        if not isinstance(value, (list, tuple)):
            raise ServiceValidationError("'weekdays' muss eine Liste von Wochentagen (1-7) sein")
        cleaned: list[int] = []
        for day in value:
            try:
                day_int = int(day)
            except (TypeError, ValueError):
                raise ServiceValidationError("'weekdays' darf nur Zahlen enthalten") from None
            if day_int < 1 or day_int > 7:
                raise ServiceValidationError("'weekdays' Werte müssen zwischen 1 und 7 liegen")
            cleaned.append(day_int)
        if not cleaned:
            raise ServiceValidationError("'weekdays' darf nicht leer sein")
        return cleaned

    def _validate_soc(value) -> int:
        try:
            soc_int = int(value)
        except (TypeError, ValueError):
            raise ServiceValidationError("'soc' muss eine Ganzzahl sein") from None
        if soc_int < 0 or soc_int > 100:
            raise ServiceValidationError("'soc' muss zwischen 0 und 100 liegen")
        return soc_int

    def _validate_active(value) -> bool:
        if not isinstance(value, bool):
            raise ServiceValidationError("'active' muss ein boolescher Wert sein")
        return value

    def _validate_precondition(value) -> int:
        if value is None:
            return 0
        if isinstance(value, bool):
            return int(value)
        try:
            precondition_int = int(value)
        except (TypeError, ValueError):
            raise ServiceValidationError("'precondition' muss bool oder 0/1 sein") from None
        if precondition_int not in (0, 1):
            raise ServiceValidationError("'precondition' muss 0 oder 1 sein")
        return precondition_int

    async def set_repeating_plan(call: ServiceCall):
        """Erstelle oder aktualisiere einen Plan"""
        coordinator = _get_coordinator()
        vehicle_id = call.data["vehicle_id"]
        plan_index = call.data.get("plan_index")

        # Hole den aktuellen EVCC-State für Validierung
        all_vehicles = await _get_vehicles(coordinator)
        _ensure_vehicle_exists(all_vehicles, vehicle_id)

        # Hole die Pläne aus dem bereits geladenen State (vermeidet zweiten API-Call)
        vehicle_data = all_vehicles.get(vehicle_id, {})
        plans = list(vehicle_data.get("repeatingPlans", []))

        new_plan = {}
        if "time" in call.data:
            new_plan["time"] = _validate_time(call.data["time"])
        if "weekdays" in call.data:
            new_plan["weekdays"] = _validate_weekdays(call.data["weekdays"])
        if "soc" in call.data:
            new_plan["soc"] = _validate_soc(call.data["soc"])
        if "active" in call.data:
            new_plan["active"] = _validate_active(call.data["active"])

        if "tz" in call.data:
            tz_val = call.data["tz"]
            if not isinstance(tz_val, str) or not tz_val:
                raise ServiceValidationError("'tz' muss eine IANA-Zeitzone sein, z.B. 'Europe/Berlin'")
            new_plan["tz"] = tz_val
        else:
            # Verwende Home Assistant Timezone als Default
            ha_tz = hass.config.time_zone
            if ha_tz:
                new_plan["tz"] = ha_tz
                _LOGGER.debug("Using HA timezone as default: %s", ha_tz)
            else:
                raise ServiceValidationError(
                    "'tz' nicht angegeben und Home Assistant Zeitzone nicht konfiguriert. "
                    "Bitte 'tz' angeben oder HA Zeitzone setzen."
                )

        # Precondition mit Default 0
        new_plan["precondition"] = _validate_precondition(call.data.get("precondition", 0))

        if plan_index is None:
            # Neuer Plan: Pflichtfelder prüfen
            required_fields = ["time", "weekdays", "soc", "active"]
            missing = [f for f in required_fields if f not in new_plan]
            if missing:
                raise ServiceValidationError(
                    "Fehlende Pflichtfelder für neuen Plan: " + ", ".join(missing)
                )

            plans.append(new_plan)
            _LOGGER.info("Added new plan for vehicle %s", vehicle_id)
        else:
            # Existierenden Plan aktualisieren (plan_index ist 1-basiert für UI)
            idx = _parse_plan_index(plan_index, len(plans))
            plans[idx] = {**plans[idx], **new_plan}
            _LOGGER.info("Updated plan %d for vehicle %s", plan_index, vehicle_id)

        await coordinator.api.set_repeating_plans(vehicle_id, plans)
        await coordinator.async_request_refresh()

        # Broadcast WebSocket-Event
        await _broadcast_plans_updated(hass, vehicle_id, plans)

    async def del_repeating_plan(call: ServiceCall):
        """Lösche einen Plan"""
        coordinator = _get_coordinator()
        vehicle_id = call.data["vehicle_id"]

        # Hole den aktuellen EVCC-State für Validierung
        all_vehicles = await _get_vehicles(coordinator)
        _ensure_vehicle_exists(all_vehicles, vehicle_id)

        # Hole die Pläne aus dem bereits geladenen State (vermeidet zweiten API-Call)
        vehicle_data = all_vehicles.get(vehicle_id, {})
        plans = list(vehicle_data.get("repeatingPlans", []))
        plan_index = _parse_plan_index(call.data.get("plan_index"), len(plans))

        plans.pop(plan_index)
        _LOGGER.info("Deleted plan %d for vehicle %s", plan_index + 1, vehicle_id)

        await coordinator.api.set_repeating_plans(vehicle_id, plans)
        await coordinator.async_request_refresh()

        # Broadcast WebSocket-Event
        await _broadcast_plans_updated(hass, vehicle_id, plans)

    hass.services.async_register(DOMAIN, "set_repeating_plan", set_repeating_plan)
    hass.services.async_register(DOMAIN, "del_repeating_plan", del_repeating_plan)


async def _broadcast_plans_updated(hass: HomeAssistant, vehicle_id: str, plans: list) -> None:
    """Sende WebSocket-Event bei Plan-Änderung"""
    from .websocket_api import EvccWebSocketAPI

    api = hass.data.get("evcc_scheduler_ws_api")
    if not api:
        return

    await api.broadcast({
        "type": "plans_updated",
        "vehicle_id": vehicle_id,
        "plans": plans
    })

