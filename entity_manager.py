import logging
from typing import Any, Callable, Dict
from homeassistant.helpers.entity_registry import async_get
from .mapping import build_entity_id

_LOGGER = logging.getLogger(__name__)


class EvccEntityManager:
    """Verwaltet dynamisches Anlegen, Aktualisieren und Löschen von Plan-Entities"""

    def __init__(self, hass: Any, async_add_entities: Callable) -> None:
        self.hass = hass
        self.async_add_entities = async_add_entities
        self.entities: Dict[str, Any] = {}
        self.registry: Any = None

    async def sync(self, data: Dict[str, Any], entity_factory: Callable) -> None:
        # Lazy-load registry beim ersten Sync
        if self.registry is None:
            self.registry = async_get(self.hass)
        
        vehicles = data.get("vehicles", {})
        _LOGGER.info("Entity sync: found %d vehicles", len(vehicles))
        wanted_ids = set()

        for vehicle_id, vehicle_data in vehicles.items():
            title = vehicle_data.get("title", vehicle_id)
            plans = vehicle_data.get("repeatingPlans", [])
            _LOGGER.info("Vehicle %s (%s) has %d plans", vehicle_id, title, len(plans))

            for idx, plan in enumerate(plans, start=1):
                unique_id = build_entity_id(vehicle_id, idx, title)
                wanted_ids.add(unique_id)

                if unique_id not in self.entities:
                    # Neue Entity erzeugen
                    try:
                        entity = entity_factory(vehicle_id, idx, plan, title)
                        self.entities[unique_id] = entity
                        self.async_add_entities([entity])
                        _LOGGER.info("Created plan entity: %s", unique_id)
                    except Exception as e:
                        _LOGGER.error("Failed to create entity %s: %s", unique_id, e)
                else:
                    # Bestehende Entity aktualisieren → sofort Switch-Status updaten
                    entity = self.entities[unique_id]
                    entity.plan = plan
                    entity.async_write_ha_state()

        # Entfernte Entities löschen + Registry bereinigen
        removed_entities = []
        for unique_id in list(self.entities.keys()):
            if unique_id not in wanted_ids:
                entity = self.entities.pop(unique_id)
                removed_entities.append(entity)
                _LOGGER.info("Removing plan entity: %s", unique_id)
        
        # Bereinige Registry async (nach dem Pop)
        for entity in removed_entities:
            if hasattr(entity, 'entity_id') and entity.entity_id:
                try:
                    await self.registry.async_remove(entity.entity_id)
                    _LOGGER.info("Removed entity_id from registry: %s", entity.entity_id)
                except Exception as e:
                    _LOGGER.debug("Could not remove entity %s from registry: %s", entity.entity_id, e)
