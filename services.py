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
        
        # Sofort die neuen Daten in den Coordinator schreiben (nicht blockierend)
        # Das gibt schnelles UI-Feedback, während der Refresh im Hintergrund läuft
        updated_data = coordinator.data or {}
        updated_vehicles = updated_data.get("vehicles", {}).copy()
        updated_vehicles[vehicle_id] = {
            "title": updated_vehicles.get(vehicle_id, {}).get("title", vehicle_id),
            "repeatingPlans": plans
        }
        coordinator.async_set_updated_data({"vehicles": updated_vehicles, "id_map": coordinator.id_map})
        _LOGGER.debug("Updated coordinator data immediately with new plans")
        
        # Trigger Refresh im Hintergrund (non-blocking) zur finalen Synchronisation
        coordinator.async_request_refresh()
        
        # Broadcast WebSocket-Event sofort (non-blocking)
        _broadcast_plans_updated(hass, vehicle_id, plans)

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
        
        # Hole die Pläne
        plans = await coordinator.api.get_repeating_plans(vehicle_id)
        
        if plan_index < 0 or plan_index >= len(plans):
            raise ServiceValidationError(f"Plan-Index {plan_index + 1} ungültig (max: {len(plans)})")
        
        # Lösche Plan lokal
        deleted_plan = plans.pop(plan_index)
        _LOGGER.info("Deleted plan %d for vehicle %s", plan_index + 1, vehicle_id)
        
        # Sende sofort zur EVCC API
        await coordinator.api.set_repeating_plans(vehicle_id, plans)
        
        # Sofort die neuen Daten in den Coordinator schreiben (nicht blockierend)
        # Das gibt schnelles UI-Feedback, während der Refresh im Hintergrund läuft
        updated_data = coordinator.data or {}
        updated_vehicles = updated_data.get("vehicles", {}).copy()
        updated_vehicles[vehicle_id] = {
            "title": updated_vehicles.get(vehicle_id, {}).get("title", vehicle_id),
            "repeatingPlans": plans
        }
        coordinator.async_set_updated_data({"vehicles": updated_vehicles, "id_map": coordinator.id_map})
        _LOGGER.debug("Updated coordinator data immediately after deletion")
        
        # Trigger Refresh im Hintergrund (non-blocking) zur finalen Synchronisation
        coordinator.async_request_refresh()
        
        # Broadcast WebSocket-Event sofort (non-blocking)
        _broadcast_plans_updated(hass, vehicle_id, plans)

    hass.services.async_register(DOMAIN, "set_repeating_plan", set_repeating_plan)
    hass.services.async_register(DOMAIN, "del_repeating_plan", del_repeating_plan)


async def _broadcast_plans_updated(hass: HomeAssistant, vehicle_id: str, plans: list) -> None:
    """Sende WebSocket-Event bei Plan-Änderung (non-blocking)"""
    from .websocket_api import EvccWebSocketAPI
    
    api = hass.data.get("evcc_scheduler_ws_api")
    if not api:
        return

    # Broadcast ist non-blocking durch api.broadcast() Design
    api.broadcast({
        "type": "plans_updated",
        "vehicle_id": vehicle_id,
        "plans": plans
    })

