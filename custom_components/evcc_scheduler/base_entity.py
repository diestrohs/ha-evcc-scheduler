import logging
from typing import Any
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from .mapping import build_entity_id

_LOGGER = logging.getLogger(__name__)


class BaseEvccPlanEntity(CoordinatorEntity):
    """Basisklasse für EVCC-Plan-Entities mit gemeinsamen Feldern und Hilfsfunktionen."""

    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, coordinator: DataUpdateCoordinator, vehicle_id: str, index: int, plan: dict, vehicle_title: str) -> None:
        super().__init__(coordinator)
        self.vehicle_id = vehicle_id
        self.index = index
        self.plan = plan
        self.vehicle_title = vehicle_title
        # Basis-ID ohne Suffix; Plattformen hängen ihr Suffix an
        self._base_id = build_entity_id(vehicle_id, index, vehicle_title)

    def update_data(self, vehicle_id: str, plan: dict, vehicle_title: str) -> None:
        """Aktualisiert gemeinsame Entity-Daten ohne Neuanlage."""
        self.vehicle_id = vehicle_id
        self.plan = plan
        self.vehicle_title = vehicle_title
        # Name bleibt vom jeweiligen Subtyp gesetzt

    def make_unique_id(self, suffix: str) -> str:
        """Erzeuge eindeutige ID basierend auf Basis-ID und Suffix."""
        if not suffix:
            return self._base_id
        return f"{self._base_id}{suffix}"

    @property
    def entity_id(self) -> str:
        """Return the entity_id directly from unique_id to bypass HA auto-naming."""
        if hasattr(self, '_attr_unique_id') and self._attr_unique_id:
            # Extract platform prefix from entity class
            platform = self.__class__.__module__.split('.')[-1]
            return f"{platform}.{self._attr_unique_id}"
        return None

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id during entity creation."""
        pass

    @property
    def extra_state_attributes(self) -> dict:
        """Gemeinsame Attribute für alle Entities."""
        return {
            "vehicle_id": self.vehicle_id,
            "vehicle_title": self.vehicle_title,
            "plan_index": self.index,
        }
