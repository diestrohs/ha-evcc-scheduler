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

        unique_id = build_entity_id("", index)
        self._attr_unique_id = unique_id
        self._attr_suggested_object_id = unique_id
        self.entity_id = f"switch.{unique_id}"
        
        # Name basierend auf HA-Sprache setzen
        language = coordinator.hass.config.language
        if language == "de":
            self._attr_name = f"EVCC wiederkehrender Plan {index}"
        else:
            self._attr_name = f"EVCC repeating plan {index}"

    def update_data(self, vehicle_id: str, plan: dict, vehicle_title: str) -> None:
        """Update entity data without recreating it (for vehicle changes)"""
        self.vehicle_id = vehicle_id
        self.plan = plan
        self.vehicle_title = vehicle_title
        self._attr_name = f"EVCC repeating Plan {self.index}"

    @property
    def is_on(self) -> bool:
        return self.plan.get("active", False)

    @property
    def extra_state_attributes(self) -> dict:
        # Reihenfolge wie in EVCC API Response: weekdays, time, tz, soc, precondition, active
        attrs = {}
        if "weekdays" in self.plan:
            attrs["weekdays"] = self.plan["weekdays"]
        if "time" in self.plan:
            attrs["time"] = self.plan["time"]
        if "tz" in self.plan:
            attrs["tz"] = self.plan["tz"]
        if "soc" in self.plan:
            attrs["soc"] = self.plan["soc"]
        if "precondition" in self.plan:
            attrs["precondition"] = self.plan["precondition"]
        if "active" in self.plan:
            attrs["active"] = self.plan["active"]
        
        # Zusätzliche Infos am Ende
        attrs["vehicle_title"] = self.vehicle_title
        attrs["vehicle_id"] = self.vehicle_id
        return attrs

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._toggle_active(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._toggle_active(False)

    async def _toggle_active(self, active: bool) -> None:
        """Toggle the plan active state and sync with EVCC API.
        
        WICHTIG: Lädt immer die aktuellen Pläne direkt von EVCC API,
        um sicherzustellen, dass EVCC die einzige Wahrheitsquelle ist.
        """
        try:
            # EVCC ist die einzige Wahrheitsquelle - hole aktuelle Pläne direkt von API
            _LOGGER.debug("Fetching current plans from EVCC for vehicle %s", self.vehicle_id)
            plans = await self.coordinator.api.get_repeating_plans(self.vehicle_id)

            # Aktualisiere nur diesen Plan
            if self.index - 1 < len(plans):
                old_state = plans[self.index - 1].get("active", False)
                plans[self.index - 1]["active"] = active
                _LOGGER.info("Toggling plan %d for vehicle '%s': %s → %s", 
                           self.index, self.vehicle_id, old_state, active)
            else:
                _LOGGER.error("Plan index %d for vehicle %s out of range (has %d plans)", 
                            self.index, self.vehicle_id, len(plans))
                return

            # Schreibe alle Pläne zurück zur API
            await self.coordinator.api.set_repeating_plans(self.vehicle_id, plans)

            # Sofort die neuen Daten in den Coordinator schreiben (nicht blockierend)
            # Das gibt schnelles UI-Feedback, während der Refresh im Hintergrund läuft
            updated_data = self.coordinator.data or {}
            updated_vehicles = updated_data.get("vehicles", {}).copy()
            updated_vehicles[self.vehicle_id] = {
                "title": updated_vehicles.get(self.vehicle_id, {}).get("title", self.vehicle_id),
                "repeatingPlans": plans
            }
            self.coordinator.async_set_updated_data({"vehicles": updated_vehicles, "id_map": self.coordinator.id_map})
            _LOGGER.debug("Updated coordinator data immediately for toggle")
            
            # Trigger Refresh im Hintergrund (non-blocking) zur finalen Synchronisation
            self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error toggling plan %d for vehicle %s: %s", self.index, self.vehicle_id, err)
            raise
