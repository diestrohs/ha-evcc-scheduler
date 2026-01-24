from .api import EvccApiClient
from .coordinator import EvccCoordinator
from .websocket_client import EvccWebsocketClient
from .websocket_api import EvccWebSocketAPI, async_register_ws_commands
from .services import async_setup_services
from .const import DOMAIN, DEFAULT_PORT, CONF_WEBSOCKET, DEFAULT_WEBSOCKET, CONF_WS_API, DEFAULT_WS_API, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
import logging

_LOGGER = logging.getLogger(__name__)

# Platforms für Plan-Attribute
PLATFORMS = ["switch", "time", "text", "number"]

async def async_setup_entry(hass, entry):
    """Richte die Integration ein"""
    _LOGGER.info("Setting up EVCC Scheduler integration")
    
    host = entry.data["host"]
    port = entry.data.get("port", DEFAULT_PORT)
    use_websocket = entry.data.get(CONF_WEBSOCKET, DEFAULT_WEBSOCKET)
    ws_api_enabled = entry.data.get(CONF_WS_API, DEFAULT_WS_API)
    poll_interval = entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

    # Erstelle API-Client
    api = EvccApiClient(host, port)
    coordinator = EvccCoordinator(hass, api, poll_interval)

    # WebSocket nur verbinden wenn aktiviert
    if use_websocket:
        async def websocket_update(data):
            _LOGGER.debug("WebSocket update received, triggering coordinator refresh")
            await coordinator.async_request_refresh()

        ws = EvccWebsocketClient(host, port, websocket_update)
        try:
            await ws.connect()
            _LOGGER.info("EVCC WebSocket client connected for instant updates")
        except Exception as err:
            _LOGGER.warning("Failed to connect WebSocket, falling back to polling: %s", err)
            ws = None
    else:
        ws = None
        _LOGGER.info("WebSocket disabled, using polling only (interval: %ds)", poll_interval)

    # Setup WebSocket API für Custom-Card (experimentell)
    if ws_api_enabled:
        ws_api = EvccWebSocketAPI(hass)
        hass.data.setdefault("evcc_scheduler_ws_api", ws_api)
        async_register_ws_commands(hass)
        _LOGGER.info("Custom Card WebSocket API enabled (experimental)")
    else:
        _LOGGER.debug("Custom Card WebSocket API disabled")

    # Speichere Coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    coordinator.ws = ws

    # Führe initialen Refresh durch (ladet alle Fahrzeuge/Pläne aus EVCC)
    # Dies ist die einzige Wahrheitsquelle - EVCC ist authorativ
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("Initial coordinator refresh completed")
    
    # Starte Switch-Platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Registriere Services
    await async_setup_services(hass)
    
    # Registriere Shutdown-Handler für sauberes Cleanup
    async def _async_shutdown(event):
        """Cleanup bei Home Assistant Shutdown"""
        _LOGGER.info("Home Assistant shutting down, cleaning up EVCC Scheduler")
        from homeassistant.helpers.entity_registry import async_get
        
        entity_registry = async_get(hass)
        entities_to_remove = [
            entity_id
            for entity_id, entity_entry in entity_registry.entities.items()
            if entity_entry.config_entry_id == entry.entry_id
        ]
        
        for entity_id in entities_to_remove:
            entity_registry.async_remove(entity_id)
        
        if entities_to_remove:
            _LOGGER.info("Removed %d entities from registry on shutdown", len(entities_to_remove))
    
    entry.async_on_unload(
        hass.bus.async_listen_once("homeassistant_stop", _async_shutdown)
    )
    
    _LOGGER.info("EVCC Scheduler integration setup completed successfully")

    return True


async def async_unload_entry(hass, entry):
    """Beende die Integration und räume auf"""
    from homeassistant.helpers.entity_registry import async_get
    
    _LOGGER.info("Unloading EVCC Scheduler integration")
    
    # Entferne alle Entities dieser Integration aus der Registry
    # Dies ist wichtig für Reload: Alle Entities werden gelöscht und beim nächsten Start neu angelegt
    entity_registry = async_get(hass)
    entities_to_remove = [
        entity_id
        for entity_id, entity_entry in entity_registry.entities.items()
        if entity_entry.config_entry_id == entry.entry_id
    ]
    
    for entity_id in entities_to_remove:
        entity_registry.async_remove(entity_id)
        _LOGGER.debug("Removed entity from registry: %s", entity_id)
    
    if entities_to_remove:
        _LOGGER.info("Removed %d entities from registry on unload", len(entities_to_remove))
    
    # Unload all platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Cleanup coordinator
    coordinator = hass.data[DOMAIN].pop(entry.entry_id)
    
    # Disconnect WebSocket
    if coordinator.ws:
        await coordinator.ws.disconnect()
        _LOGGER.debug("WebSocket connection closed")
    
    # Close API client
    await coordinator.api.close()
    
    # Cleanup WebSocket API für Custom-Card
    ws_api = hass.data.pop("evcc_scheduler_ws_api", None)
    if ws_api:
        await ws_api.close_all()
        _LOGGER.debug("WebSocket API closed")
    
    _LOGGER.info("EVCC Scheduler integration unloaded successfully")
    
    return unload_ok
