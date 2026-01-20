from .api import EvccApiClient
from .coordinator import EvccCoordinator
from .websocket_client import EvccWebsocketClient
from .websocket_api import EvccWebSocketAPI, async_register_ws_commands
from .services import async_setup_services
from .const import DOMAIN, DEFAULT_PORT
import logging

_LOGGER = logging.getLogger(__name__)

# Aktuell nur Switch-Platform
PLATFORMS = ["switch"]

async def async_setup_entry(hass, entry):
    host = entry.data["host"]
    port = entry.data.get("port", DEFAULT_PORT)

    api = EvccApiClient(host, port)
    coordinator = EvccCoordinator(hass, api)

    async def websocket_update(data):
        _LOGGER.debug("WebSocket update received, triggering coordinator refresh")
        await coordinator.async_request_refresh()

    ws = EvccWebsocketClient(host, port, websocket_update)
    await ws.connect()
    _LOGGER.info("EVCC WebSocket client connected for instant updates")

    # Setup WebSocket API für Custom-Card
    ws_api = EvccWebSocketAPI(hass)
    hass.data.setdefault("evcc_scheduler_ws_api", ws_api)
    async_register_ws_commands(hass)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    coordinator.ws = ws

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Services registrieren
    await async_setup_services(hass)

    return True


async def async_unload_entry(hass, entry):
    from homeassistant.helpers.entity_registry import async_get
    
    # Entferne alle Entities dieser Integration aus der Registry
    entity_registry = async_get(hass)
    entities = entity_registry.entities
    
    entities_to_remove = [
        entity_id
        for entity_id, entity_entry in entities.items()
        if entity_entry.config_entry_id == entry.entry_id
    ]
    
    for entity_id in entities_to_remove:
        entity_registry.async_remove(entity_id)
        _LOGGER.info("Removed entity from registry on unload: %s", entity_id)
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    coordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.ws.disconnect()
    await coordinator.api.close()
    
    # Cleanup WebSocket API
    ws_api = hass.data.pop("evcc_scheduler_ws_api", None)
    if ws_api:
        await ws_api.close_all()
    
    return unload_ok
