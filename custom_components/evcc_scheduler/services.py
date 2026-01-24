import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_services(hass: HomeAssistant):
    """Registriere Services für Plan-Verwaltung"""

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

    async def set_repeating_plan(call: ServiceCall):
        """Erstelle oder aktualisiere einen Plan"""
        coordinator = list(hass.data[DOMAIN].values())[0]
        vehicle_id = call.data["vehicle_id"]
        plan_index = call.data.get("plan_index")

        # Hole den aktuellen EVCC-State für Validierung
        all_vehicles = await _get_vehicles(coordinator)
        _ensure_vehicle_exists(all_vehicles, vehicle_id)

        # Hole die Pläne aus dem bereits geladenen State (vermeidet zweiten API-Call)
        vehicle_data = all_vehicles.get(vehicle_id, {})
        plans = list(vehicle_data.get("repeatingPlans", []))

        new_plan = {}
        for key in ["time", "weekdays", "soc", "active"]:
            if key in call.data:
                new_plan[key] = call.data[key]

        if plan_index is None:
            # Neuen Plan anhängen
            plans.append(new_plan)
            _LOGGER.info("Added new plan for vehicle %s", vehicle_id)
        else:
            # Existierenden Plan aktualisieren (plan_index ist 1-basiert für UI)
            idx = int(plan_index) - 1
            if 0 <= idx < len(plans):
                plans[idx] = {**plans[idx], **new_plan}
                _LOGGER.info("Updated plan %d for vehicle %s", plan_index, vehicle_id)
            else:
                raise ServiceValidationError(f"Plan-Index {plan_index} ungültig")

        await coordinator.api.set_repeating_plans(vehicle_id, plans)
        await coordinator.async_request_refresh()

        # Broadcast WebSocket-Event
        await _broadcast_plans_updated(hass, vehicle_id, plans)

    async def del_repeating_plan(call: ServiceCall):
        """Lösche einen Plan"""
        coordinator = list(hass.data[DOMAIN].values())[0]
        vehicle_id = call.data["vehicle_id"]
        plan_index = int(call.data["plan_index"]) - 1  # Konvertiere 1-basiert zu 0-basiert

        # Hole den aktuellen EVCC-State für Validierung
        all_vehicles = await _get_vehicles(coordinator)
        _ensure_vehicle_exists(all_vehicles, vehicle_id)

        # Hole die Pläne aus dem bereits geladenen State (vermeidet zweiten API-Call)
        vehicle_data = all_vehicles.get(vehicle_id, {})
        plans = list(vehicle_data.get("repeatingPlans", []))
        if 0 <= plan_index < len(plans):
            plans.pop(plan_index)
            _LOGGER.info("Deleted plan %d for vehicle %s", plan_index + 1, vehicle_id)
        else:
            raise ServiceValidationError(f"Plan-Index {plan_index + 1} ungültig")

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

