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
        # Lazy-load registry nur wenn tatsächlich benötigt
        vehicles = data.get("vehicles", {})
        _LOGGER.debug("Entity sync: found %d vehicles", len(vehicles))
        
        # Sammle alle gewünschten Plan-Indices (vehicle-agnostic)
        plan_count = 0
        current_vehicle_id = None
        current_vehicle_title = None
        all_plans = []
        
        for vehicle_id, vehicle_data in vehicles.items():
            title = vehicle_data.get("title", vehicle_id)
            plans = vehicle_data.get("repeatingPlans", [])
            if plans:
                current_vehicle_id = vehicle_id
                current_vehicle_title = title
                all_plans = plans
                plan_count = len(plans)
                _LOGGER.debug("Vehicle %s (%s) has %d plans", vehicle_id, title, plan_count)
                break  # Nur ein Fahrzeug aktiv in EVCC
        
        # Bestimme gewünschte Entity-IDs basierend auf Plan-Anzahl
        wanted_ids = {build_entity_id("", idx) for idx in range(1, plan_count + 1)}
        current_ids = set(self.entities.keys())
        
        to_add = wanted_ids - current_ids
        to_remove = current_ids - wanted_ids
        to_update = wanted_ids & current_ids
        
        # 1. Update bestehende Entities (kein Registry-Zugriff)
        if current_vehicle_id and to_update:
            for idx in range(1, plan_count + 1):
                unique_id = build_entity_id("", idx)
                if unique_id in self.entities:
                    entity = self.entities[unique_id]
                    plan = all_plans[idx - 1]
                    entity.update_data(current_vehicle_id, plan, current_vehicle_title)
                    entity.async_write_ha_state()
                    _LOGGER.debug("Updated plan entity: %s", unique_id)
        
        # 2. Neue Entities anlegen (nur wenn mehr Pläne)
        if to_add and current_vehicle_id:
            new_entities = []
            for idx in range(1, plan_count + 1):
                unique_id = build_entity_id("", idx)
                if unique_id in to_add:
                    try:
                        plan = all_plans[idx - 1]
                        entity = entity_factory(current_vehicle_id, idx, plan, current_vehicle_title)
                        self.entities[unique_id] = entity
                        new_entities.append(entity)
                        _LOGGER.info("Created plan entity: %s", unique_id)
                    except Exception as e:
                        _LOGGER.error("Failed to create entity %s: %s", unique_id, e)
            if new_entities:
                self.async_add_entities(new_entities)
        
        # 3. Überschüssige Entities löschen (nur wenn weniger Pläne)
        if to_remove:
            # Lazy-load registry nur wenn tatsächlich gelöscht wird
            if self.registry is None:
                self.registry = async_get(self.hass)
            
            # Entferne sofort aus lokalem Cache
            removed_entities = []
            for unique_id in to_remove:
                if unique_id in self.entities:
                    entity = self.entities.pop(unique_id)
                    removed_entities.append(entity)
                    _LOGGER.info("Removing plan entity: %s", unique_id)
            
            # Registr-Cleanup IM HINTERGRUND (non-blocking)
            # Das erlaubt der UI sofort zu aktualisieren
            async def cleanup_registry():
                for entity in removed_entities:
                    if hasattr(entity, 'entity_id') and entity.entity_id:
                        try:
                            self.registry.async_remove(entity.entity_id)
                            _LOGGER.debug("Removed entity_id from registry: %s", entity.entity_id)
                        except Exception as e:
                            _LOGGER.debug("Could not remove entity %s from registry: %s", entity.entity_id, e)
            
            # Schedule im Hintergrund
            self.hass.async_create_task(cleanup_registry())
