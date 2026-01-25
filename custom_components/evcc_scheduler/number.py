import logging
from typing import Any, Callable
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from .entity_manager import EvccEntityManager, setup_platform
from .base_entity import BaseEvccPlanEntity
from .mapping import build_entity_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: Any, entry: Any, async_add_entities: Callable) -> bool:
    """Richte Number-Platform auf"""
    coordinator: DataUpdateCoordinator = hass.data["evcc_scheduler"][entry.entry_id]
    return await setup_platform(
        hass,
        entry,
        async_add_entities,
        suffix="_soc",
        entity_factory=lambda vehicle_id, idx, plan, title: EvccPlanSoc(coordinator, vehicle_id, idx, plan, title),
        logger=_LOGGER,
        platform_name="number",
    )


class EvccPlanSoc(BaseEvccPlanEntity, NumberEntity):
    _attr_translation_key = "repeating_plan_soc"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 10
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:battery-charging"
    
    def __init__(self, coordinator: DataUpdateCoordinator, vehicle_id: str, index: int, plan: dict, vehicle_title: str) -> None:
        super().__init__(coordinator, vehicle_id, index, plan, vehicle_title)
        unique_id = self.make_unique_id("_soc")
        self._attr_unique_id = unique_id
        self._attr_suggested_object_id = unique_id

    # update_data geerbt von BaseEvccPlanEntity

    @property
    def native_value(self) -> float | None:
        return self.plan.get("soc")

    async def async_set_native_value(self, value: float) -> None:
        """Set new SOC value"""
        try:
            soc = int(value)
            
            if not 0 <= soc <= 100:
                _LOGGER.error("Invalid SOC value: must be between 0 and 100")
                return
            
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
                plans[self.index - 1]["soc"] = soc
                _LOGGER.info("Setting SOC for plan %d of vehicle '%s' to %d%%", self.index, self.vehicle_id, soc)
            else:
                _LOGGER.error("Plan index %d out of range", self.index)
                return

            await self.coordinator.api.set_repeating_plans(self.vehicle_id, plans)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting SOC for plan %d: %s", self.index, err)
            raise

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "vehicle_id": self.vehicle_id,
            "vehicle_title": self.vehicle_title,
            "plan_index": self.index
        }
