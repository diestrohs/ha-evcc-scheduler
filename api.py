import aiohttp
import logging
from typing import Any, Dict, List

_LOGGER = logging.getLogger(__name__)

class EvccApiClient:
    def __init__(self, host: str, port: int) -> None:
        self.base_url = f"http://{host}:{port}/api"
        self.session: aiohttp.ClientSession | None = None
        _LOGGER.info("EVCC API Base URL: %s", self.base_url)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create a persistent session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self) -> None:
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_state(self) -> Dict[str, Any]:
        """Get the complete system state from EVCC."""
        session = await self._get_session()
        url = f"{self.base_url}/state"
        try:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientResponseError as e:
            _LOGGER.error("API Error fetching state - Status: %d", e.status)
            raise

    async def get_repeating_plans(self, vehicle_id: str) -> List[Dict[str, Any]]:
        """Get repeating plans for a vehicle.
        
        Note: The repeating plans are retrieved from the /state endpoint
        since there's no direct GET endpoint for repeating plans.
        """
        session = await self._get_session()
        state = await self.get_state()
        
        # Extract the repeating plans from the state for this vehicle
        vehicles = state.get("vehicles", {})
        if vehicle_id in vehicles:
            vehicle_data = vehicles[vehicle_id]
            plans = vehicle_data.get("repeatingPlans", [])
            _LOGGER.debug("Retrieved %d repeating plans for vehicle %s", len(plans), vehicle_id)
            return plans
        
        _LOGGER.error("Vehicle %s not found in state", vehicle_id)
        raise ValueError(f"Vehicle {vehicle_id} not found")

    async def set_repeating_plans(self, vehicle_id: str, plans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Set repeating plans for a vehicle.
        
        EVCC API endpoint: POST /vehicles/{vehicle_id}/plan/repeating
        The vehicle_id (e.g., "db:1") is used directly in the URL path.
        """
        session = await self._get_session()
        
        # Build URL using the vehicle_id directly (e.g., "db:1")
        # Note: aiohttp handles the URL correctly without manual encoding
        url = f"{self.base_url}/vehicles/{vehicle_id}/plan/repeating"
        
        _LOGGER.info("Setting %d repeating plans for vehicle %s", len(plans), vehicle_id)
        
        try:
            async with session.post(url, json=plans) as resp:
                resp.raise_for_status()
                result = await resp.json()
                _LOGGER.info("Successfully updated repeating plans for vehicle %s", vehicle_id)
                return result if result else plans
        except aiohttp.ClientResponseError as e:
            _LOGGER.error("API Error setting plans for vehicle %s - Status: %d", vehicle_id, e.status)
            raise
        except Exception as e:
            _LOGGER.error("Unexpected error setting plans for vehicle %s: %s", vehicle_id, str(e))
            raise
