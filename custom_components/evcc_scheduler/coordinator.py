import logging
from datetime import timedelta
from typing import Any, Dict
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import EvccApiClient
from .mapping import extract_plans
from .const import DEFAULT_POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)

class EvccCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: Any, api: EvccApiClient, poll_interval: int = DEFAULT_POLL_INTERVAL) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="evcc_scheduler",
            update_interval=timedelta(seconds=poll_interval),
        )
        self.api = api
        self.id_map: Dict[str, str] = {}
    
    
    async def _async_update_data(self) -> Dict[str, Any]:
        _LOGGER.debug("Fetching EVCC state and plans")
        state = await self.api.get_state()
        
        # Hole vehicleName aus den Loadpoints
        active_vehicle_id = None
        loadpoints = state.get("loadpoints", [])
        
        for loadpoint in loadpoints:
            vehicle_name = loadpoint.get("vehicleName", "")
            # Wenn vehicleName gesetzt ist (nicht leer), verwende dieses Fahrzeug
            if vehicle_name:
                active_vehicle_id = vehicle_name
                _LOGGER.info("Active vehicle: %s", active_vehicle_id)
                break
        
        # Lade nur Pläne für das aktive Fahrzeug
        vehicles_data = {}
        all_vehicles = state.get("vehicles", {})
        
        if active_vehicle_id and active_vehicle_id in all_vehicles:
            # Nur das aktive Fahrzeug laden
            vehicle = all_vehicles[active_vehicle_id]
            title = vehicle.get("title", active_vehicle_id)
            plans = vehicle.get("repeatingPlans", [])
            
            vehicles_data[active_vehicle_id] = {
                "title": title,
                "repeatingPlans": plans if isinstance(plans, list) else []
            }
            
            # Data-Consistency-Log: Bestätige aktuellen State
            _LOGGER.debug(
                "Data consistency check: Vehicle %s (%s) has %d plans",
                active_vehicle_id, title, len(plans)
            )
            self.id_map = {active_vehicle_id: title}
            _LOGGER.debug("Loaded %d plans for active vehicle: %s (%s)", len(plans), title, active_vehicle_id)
        else:
            # Kein Fahrzeug ausgewählt oder nicht gefunden
            self.id_map = {}
            if not active_vehicle_id:
                _LOGGER.info("No vehicle selected in EVCC (vehicleName is empty)")
            else:
                _LOGGER.warning("Vehicle %s not found in EVCC vehicles data", active_vehicle_id)
        
        return {"vehicles": vehicles_data, "id_map": self.id_map}
