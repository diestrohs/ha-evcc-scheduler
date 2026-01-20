import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_services(hass: HomeAssistant):
    """Registriere Services für Plan-Verwaltung"""

    async def set_repeating_plan(call: ServiceCall):
        """Erstelle oder aktualisiere einen Plan"""
        coordinator = list(hass.data[DOMAIN].values())[0]
        vehicle_id = call.data["vehicle_id"]
        plan_index = call.data.get("plan_index")
        
        # Hole den aktuellen EVCC-State für Validierung
        evcc_state = await coordinator.api.get_state()
        all_vehicles = evcc_state.get("vehicles", {})
        loadpoints = evcc_state.get("loadpoints", [])
        
        # Finde das aktiv gewählte Fahrzeug in EVCC
        active_vehicle_id = None
        for loadpoint in loadpoints:
            vehicle_name = loadpoint.get("vehicleName", "")
            if vehicle_name:
                active_vehicle_id = vehicle_name
                break
        
        # Validierungen
        if not active_vehicle_id:
            raise ServiceValidationError("Kein Fahrzeug in EVCC gewählt")
        
        if vehicle_id != active_vehicle_id:
            raise ServiceValidationError(
                f"Die Fahrzeug-ID '{vehicle_id}' stimmt nicht mit der gewählten "
                f"Fahrzeug-ID in EVCC '{active_vehicle_id}' überein"
            )
        
        if vehicle_id not in all_vehicles:
            available_vehicles = ", ".join(all_vehicles.keys()) if all_vehicles else "keine"
            raise ServiceValidationError(
                f"Das Fahrzeug '{vehicle_id}' ist in EVCC nicht angelegt. "
                f"Verfügbare Fahrzeuge: {available_vehicles}"
            )
        
        # Hole die Pläne und aktualisiere
        plans = await coordinator.api.get_repeating_plans(vehicle_id)

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
        evcc_state = await coordinator.api.get_state()
        all_vehicles = evcc_state.get("vehicles", {})
        loadpoints = evcc_state.get("loadpoints", [])
        
        # Finde das aktiv gewählte Fahrzeug in EVCC
        active_vehicle_id = None
        for loadpoint in loadpoints:
            vehicle_name = loadpoint.get("vehicleName", "")
            if vehicle_name:
                active_vehicle_id = vehicle_name
                break
        
        # Validierungen
        if not active_vehicle_id:
            raise ServiceValidationError("Kein Fahrzeug in EVCC gewählt")
        
        if vehicle_id != active_vehicle_id:
            raise ServiceValidationError(
                f"Die Fahrzeug-ID '{vehicle_id}' stimmt nicht mit der gewählten "
                f"Fahrzeug-ID in EVCC '{active_vehicle_id}' überein"
            )
        
        if vehicle_id not in all_vehicles:
            available_vehicles = ", ".join(all_vehicles.keys()) if all_vehicles else "keine"
            raise ServiceValidationError(
                f"Das Fahrzeug '{vehicle_id}' ist in EVCC nicht angelegt. "
                f"Verfügbare Fahrzeuge: {available_vehicles}"
            )

        plans = await coordinator.api.get_repeating_plans(vehicle_id)
        if 0 <= plan_index < len(plans):
            plans.pop(plan_index)
            _LOGGER.info("Deleted plan %d for vehicle %s", plan_index + 1, vehicle_id)
        else:
            raise ServiceValidationError(f"Plan-Index {plan_index + 1} ungültig")

        await coordinator.api.set_repeating_plans(vehicle_id, plans)
        await coordinator.async_request_refresh()
        
        # Broadcast WebSocket-Event
        await _broadcast_plans_updated(hass, vehicle_id, plans)

    async def toggle_plan_active(call: ServiceCall):
        """Toggle Active-Status eines Plans"""
        coordinator = list(hass.data[DOMAIN].values())[0]
        vehicle_id = call.data["vehicle_id"]
        plan_index = int(call.data["plan_index"]) - 1  # Konvertiere 1-basiert zu 0-basiert
        active = call.data.get("active")

        # Hole den aktuellen EVCC-State für Validierung
        evcc_state = await coordinator.api.get_state()
        all_vehicles = evcc_state.get("vehicles", {})
        loadpoints = evcc_state.get("loadpoints", [])
        
        # Finde das aktiv gewählte Fahrzeug in EVCC
        active_vehicle_id = None
        for loadpoint in loadpoints:
            vehicle_name = loadpoint.get("vehicleName", "")
            if vehicle_name:
                active_vehicle_id = vehicle_name
                break
        
        # Validierungen
        if not active_vehicle_id:
            raise ServiceValidationError("Kein Fahrzeug in EVCC gewählt")
        
        if vehicle_id != active_vehicle_id:
            raise ServiceValidationError(
                f"Die Fahrzeug-ID '{vehicle_id}' stimmt nicht mit der gewählten "
                f"Fahrzeug-ID in EVCC '{active_vehicle_id}' überein"
            )
        
        if vehicle_id not in all_vehicles:
            available_vehicles = ", ".join(all_vehicles.keys()) if all_vehicles else "keine"
            raise ServiceValidationError(
                f"Das Fahrzeug '{vehicle_id}' ist in EVCC nicht angelegt. "
                f"Verfügbare Fahrzeuge: {available_vehicles}"
            )

        plans = await coordinator.api.get_repeating_plans(vehicle_id)
        if 0 <= plan_index < len(plans):
            if active is not None:
                plans[plan_index]["active"] = active
            else:
                plans[plan_index]["active"] = not plans[plan_index].get("active", False)
            _LOGGER.info("Toggled plan %d for vehicle %s to %s", plan_index + 1, vehicle_id, plans[plan_index]["active"])
        else:
            raise ServiceValidationError(f"Plan-Index {plan_index + 1} ungültig")

        await coordinator.api.set_repeating_plans(vehicle_id, plans)
        await coordinator.async_request_refresh()
        
        # Broadcast WebSocket-Event
        await _broadcast_plans_updated(hass, vehicle_id, plans)

    hass.services.async_register(DOMAIN, "set_repeating_plan", set_repeating_plan)
    hass.services.async_register(DOMAIN, "del_repeating_plan", del_repeating_plan)
    hass.services.async_register(DOMAIN, "toggle_plan_active", toggle_plan_active)


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

