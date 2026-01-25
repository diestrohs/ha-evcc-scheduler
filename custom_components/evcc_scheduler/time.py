import logging
from typing import Any, Callable
from datetime import time as dt_time
from homeassistant.components.time import TimeEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from .entity_manager import EvccEntityManager, setup_platform
from .base_entity import BaseEvccPlanEntity
from .mapping import build_entity_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: Any, entry: Any, async_add_entities: Callable) -> bool:
    """Richte Time-Platform auf"""
    coordinator: DataUpdateCoordinator = hass.data["evcc_scheduler"][entry.entry_id]
    return await setup_platform(
        hass,
        entry,
        async_add_entities,
        suffix="_time",
        entity_factory=lambda vehicle_id, idx, plan, title: EvccPlanTime(coordinator, vehicle_id, idx, plan, title),
        logger=_LOGGER,
        platform_name="time",
    )


class EvccPlanTime(BaseEvccPlanEntity, TimeEntity):
    _attr_translation_key = "repeating_plan_time"
    _attr_icon = "mdi:clock-digital"
    
    def __init__(self, coordinator: DataUpdateCoordinator, vehicle_id: str, index: int, plan: dict, vehicle_title: str) -> None:
        super().__init__(coordinator, vehicle_id, index, plan, vehicle_title)
        unique_id = self.make_unique_id("_time")
        self._attr_unique_id = unique_id
        self._attr_suggested_object_id = unique_id
        self.entity_id = f"time.{unique_id}"

    # update_data geerbt von BaseEvccPlanEntity

    @property
    def native_value(self) -> dt_time | None:
        time_str = self.plan.get("time")
        if not time_str:
            return None
        try:
            hour, minute = map(int, time_str.split(":"))
            return dt_time(hour=hour, minute=minute)
        except (ValueError, AttributeError):
            return None

    async def async_set_value(self, value: dt_time) -> None:
        """Set new time value"""
        try:
            time_str = value.strftime("%H:%M")
            
            coordinator_data = self.coordinator.data
            if not coordinator_data or "vehicles" not in coordinator_data:
                _LOGGER.error("No coordinator data available")
                return

            vehicles = coordinator_data.get("vehicles", {})
            if self.vehicle_id not in vehicles:
                _LOGGER.error("Vehicle %s not found", self.vehicle_id)
                return

            vehicle_data = vehicles[self.vehicle_id]
            plans = vehicle_data.get("repeatingPlans", [])

            if self.index - 1 < len(plans):
                plans[self.index - 1]["time"] = time_str
                _LOGGER.info("Setting time for plan %d of vehicle '%s' to %s", self.index, self.vehicle_id, time_str)
            else:
                _LOGGER.error("Plan index %d out of range", self.index)
                return

            await self.coordinator.api.set_repeating_plans(self.vehicle_id, plans)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting time for plan %d: %s", self.index, err)
            raise

    # Gemeinsame extra_state_attributes werden aus der Basisklasse bereitgestellt
