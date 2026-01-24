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
        
        # Lade Pläne für ALLE Fahrzeuge
        vehicles_data = {}
        all_vehicles = state.get("vehicles", {})
        
        for vehicle_id, vehicle_data in all_vehicles.items():
            if not isinstance(vehicle_data, dict):
                continue
                
            title = vehicle_data.get("title", vehicle_id)
            plans = vehicle_data.get("repeatingPlans", [])
            
            vehicles_data[vehicle_id] = {
                "title": title,
                "repeatingPlans": plans if isinstance(plans, list) else []
            }
            
            self.id_map[vehicle_id] = title
            _LOGGER.debug("Loaded %d plans for vehicle: %s (%s)", len(plans), title, vehicle_id)
        
        if not vehicles_data:
            _LOGGER.info("No vehicles found in EVCC")
            self.id_map = {}
        
        return {"vehicles": vehicles_data, "id_map": self.id_map}
