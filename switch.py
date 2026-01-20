import logging
from typing import Any, Callable
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from .entity_manager import EvccEntityManager
from .mapping import build_entity_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: Any, entry: Any, async_add_entities: Callable) -> bool:
    coordinator: DataUpdateCoordinator = hass.data["evcc_scheduler"][entry.entry_id]
    manager = EvccEntityManager(hass, async_add_entities)

    async def async_sync() -> None:
        await manager.sync(
            coordinator.data,
            lambda vehicle_id, idx, plan, title: EvccPlanSwitch(coordinator, vehicle_id, idx, plan, title),
        )

    # Callback für Coordinator-Updates
    def handle_update() -> None:
        hass.async_create_task(async_sync())

    coordinator.async_add_listener(handle_update)

    # Initialer Sync (first_refresh wurde bereits in __init__.py aufgerufen)
    await async_sync()

    return True


class EvccPlanSwitch(CoordinatorEntity, SwitchEntity):
    _attr_should_poll = False
    
    def __init__(self, coordinator: DataUpdateCoordinator, vehicle_id: str, index: int, plan: dict, vehicle_title: str) -> None:
        super().__init__(coordinator)
        self.vehicle_id = vehicle_id
        self.index = index
        self.plan = plan
        self.vehicle_title = vehicle_title

        unique_id = build_entity_id(vehicle_id, index, vehicle_title)
        self._attr_unique_id = unique_id
        # Force predictable entity_id (object_id) while keeping a friendly name
        self._attr_suggested_object_id = unique_id
        # Fallback: force entity_id for brand-new entities (registry overrides if already present)
        self.entity_id = f"switch.{unique_id}"
        self._attr_name = f"{vehicle_title} repeating Plan {index:02d}"

    @property
    def is_on(self) -> bool:
        return self.plan.get("active", False)

    @property
    def extra_state_attributes(self) -> dict:
        return self.plan.copy()

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._toggle_active(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._toggle_active(False)

    async def _toggle_active(self, active: bool) -> None:
        """Toggle the plan active state and sync with EVCC API."""
        try:
            # Lade alle Pläne vom Fahrzeug aus dem Coordinator (nicht von der API!)
            # Dies ist effizienter als einen zusätzlichen API-Call zu machen
            coordinator_data = self.coordinator.data
            if not coordinator_data or "vehicles" not in coordinator_data:
                _LOGGER.error("No coordinator data available for vehicle %s", self.vehicle_id)
                return
            
            vehicles = coordinator_data.get("vehicles", {})
            if self.vehicle_id not in vehicles:
                _LOGGER.error("Vehicle %s not found in coordinator data", self.vehicle_id)
                return
            
            vehicle_data = vehicles[self.vehicle_id]
            plans = vehicle_data.get("repeatingPlans", [])

            # Aktualisiere nur diesen Plan
            if self.index - 1 < len(plans):
                plans[self.index - 1]["active"] = active
                _LOGGER.info("Toggling plan %d for vehicle '%s' to %s", self.index, self.vehicle_id, active)
            else:
                _LOGGER.error("Plan index %d for vehicle %s out of range", self.index, self.vehicle_id)
                return

            # Schreibe alle Pläne zurück zur API
            await self.coordinator.api.set_repeating_plans(self.vehicle_id, plans)

            # Refresh Coordinator → alle Entities updaten
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error toggling plan %d for vehicle %s: %s", self.index, self.vehicle_id, err)
            raise
