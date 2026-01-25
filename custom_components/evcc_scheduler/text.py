import logging
from typing import Any, Callable
from homeassistant.components.text import TextEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from .entity_manager import EvccEntityManager, setup_platform
from .base_entity import BaseEvccPlanEntity
from .mapping import build_entity_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: Any, entry: Any, async_add_entities: Callable) -> bool:
    """Richte Text-Platform auf"""
    coordinator: DataUpdateCoordinator = hass.data["evcc_scheduler"][entry.entry_id]
    return await setup_platform(
        hass,
        entry,
        async_add_entities,
        suffix="_weekdays",
        entity_factory=lambda vehicle_id, idx, plan, title: EvccPlanWeekdays(coordinator, vehicle_id, idx, plan, title),
        logger=_LOGGER,
        platform_name="text",
    )


class EvccPlanWeekdays(BaseEvccPlanEntity, TextEntity):
    _attr_translation_key = "repeating_plan_weekdays"
    
    def __init__(self, coordinator: DataUpdateCoordinator, vehicle_id: str, index: int, plan: dict, vehicle_title: str) -> None:
        super().__init__(coordinator, vehicle_id, index, plan, vehicle_title)
        unique_id = self.make_unique_id("_weekdays")
        self._attr_unique_id = unique_id
        self._attr_suggested_object_id = unique_id
        self.entity_id = f"text.{unique_id}"

    # update_data geerbt von BaseEvccPlanEntity

    @property
    def native_value(self) -> str:
        weekdays = self.plan.get("weekdays", [])
        if not weekdays:
            return ""
        # Konvertiere Liste zu kommagetrennt: [1, 2, 3] -> "1,2,3"
        return ",".join(str(day) for day in weekdays)

    async def async_set_value(self, value: str) -> None:
        """Set new weekdays value"""
        try:
            # Konvertiere "1,2,3" -> [1, 2, 3]
            weekdays = [int(day.strip()) for day in value.split(",") if day.strip()]
            
            # Validiere Werte (1-7)
            if not all(1 <= day <= 7 for day in weekdays):
                _LOGGER.error("Invalid weekdays: must be between 1 and 7")
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
                plans[self.index - 1]["weekdays"] = weekdays
                _LOGGER.info("Setting weekdays for plan %d of vehicle '%s' to %s", self.index, self.vehicle_id, weekdays)
            else:
                _LOGGER.error("Plan index %d out of range", self.index)
                return

            await self.coordinator.api.set_repeating_plans(self.vehicle_id, plans)
            await self.coordinator.async_request_refresh()
        except ValueError as err:
            _LOGGER.error("Invalid weekdays format: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Error setting weekdays for plan %d: %s", self.index, err)
            raise

    @property
    def extra_state_attributes(self) -> dict:
        attrs = super().extra_state_attributes
        attrs["weekdays_list"] = self.plan.get("weekdays", [])
        return attrs
