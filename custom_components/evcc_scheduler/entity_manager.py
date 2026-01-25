import logging
from typing import Any, Callable, Dict
from homeassistant.helpers.entity_registry import async_get
from .mapping import build_entity_id

_LOGGER = logging.getLogger(__name__)


class EvccEntityManager:
    """Verwaltet dynamisches Anlegen, Aktualisieren und Löschen von Plan-Entities"""

    def __init__(self, hass: Any, async_add_entities: Callable, suffix: str = "") -> None:
        self.hass = hass
        self.async_add_entities = async_add_entities
        self.suffix = suffix
        self.entities: Dict[str, Any] = {}
        # Registry einmalig initialisieren (statt Lazy-Load bei jedem Sync)
        try:
            self.registry = async_get(self.hass)
        except Exception:
            self.registry = None

    async def sync(self, data: Dict[str, Any], entity_factory: Callable) -> None:

        vehicles = data.get("vehicles", {})
        _LOGGER.debug("Entity sync (%s): found %d vehicles", self.suffix or "switch", len(vehicles))
        wanted_ids = set()

        for vehicle_id, vehicle_data in vehicles.items():
            title = vehicle_data.get("title", vehicle_id)
            plans = vehicle_data.get("repeatingPlans", [])

            for idx, plan in enumerate(plans, start=1):
                base_id = build_entity_id(vehicle_id, idx, title)
                # Suffix wird direkt angehängt an base_id
                unique_id = f"{base_id}{self.suffix}" if self.suffix else base_id
                wanted_ids.add(unique_id)

                if unique_id not in self.entities:
                    # Neue Entity erzeugen
                    try:
                        entity = entity_factory(vehicle_id, idx, plan, title)
                        self.entities[unique_id] = entity
                        self.async_add_entities([entity])
                        _LOGGER.debug("Created entity: %s", unique_id)
                    except Exception as e:
                        _LOGGER.error("Failed to create entity %s: %s", unique_id, e)
                else:
                    # Bestehende Entity aktualisieren
                    entity = self.entities[unique_id]
                    entity.plan = plan
                    entity.async_write_ha_state()

        # Entfernte Entities löschen + Registry bereinigen
        removed_entities = []
        for unique_id in list(self.entities.keys()):
            if unique_id not in wanted_ids:
                entity = self.entities.pop(unique_id)
                removed_entities.append(entity)
                _LOGGER.debug("Removing entity: %s", unique_id)

        # Bereinige Registry async (nach dem Pop)
        for entity in removed_entities:
            if hasattr(entity, 'entity_id') and entity.entity_id:
                try:
                    await self.registry.async_remove(entity.entity_id)
                    _LOGGER.debug("Removed entity_id from registry: %s", entity.entity_id)        
                except Exception as e:
                    _LOGGER.debug("Could not remove entity %s from registry: %s", entity.entity_id, e)


async def setup_platform(
    hass: Any,
    entry: Any,
    async_add_entities: Callable,
    suffix: str,
    entity_factory: Callable[[str, int, Dict[str, Any], str], Any],
    logger: Any,
    platform_name: str,
) -> bool:
    """Gemeinsame Setup-Logik für Plattformen (switch/time/text/number)."""
    coordinator = hass.data["evcc_scheduler"][entry.entry_id]
    manager = EvccEntityManager(hass, async_add_entities, suffix=suffix)
    logger.debug("%s platform setup started", platform_name)

    async def async_sync() -> None:
        await manager.sync(
            coordinator.data,
            lambda vehicle_id, idx, plan, title: entity_factory(vehicle_id, idx, plan, title),
        )

    def handle_update() -> None:
        logger.debug("Coordinator update received, syncing %s entities", platform_name)
        hass.async_create_task(async_sync())

    coordinator.async_add_listener(handle_update)
    await async_sync()

    logger.info("%s platform setup completed", platform_name)
    return True
