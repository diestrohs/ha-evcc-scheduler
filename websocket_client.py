import asyncio
import json
import logging
import websockets

_LOGGER = logging.getLogger(__name__)

class EvccWebsocketClient:
    def __init__(self, host, port, coordinator_callback):
        self.url = f"ws://{host}:{port}/ws"
        self.coordinator_callback = coordinator_callback
        self._task = None
        self._ws = None
        self._running = False

    async def connect(self):
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def disconnect(self):
        self._running = False
        if self._ws:
            await self._ws.close()
        if self._task:
            self._task.cancel()

    async def _run(self):
        while self._running:
            try:
                async with websockets.connect(self.url) as ws:
                    self._ws = ws
                    _LOGGER.info("Connected to EVCC websocket at %s", self.url)

                    async for msg in ws:
                        try:
                            data = json.loads(msg)
                            
                            # Filtere relevante Nachrichten für sofortiges Update
                            # EVCC sendet verschiedene Event-Typen
                            if self._is_relevant_update(data):
                                _LOGGER.debug("Relevant WS message received, triggering coordinator refresh")
                                await self.coordinator_callback(data)
                        except json.JSONDecodeError:
                            _LOGGER.debug("Non-JSON websocket message ignored")
                        except Exception as e:
                            _LOGGER.error("Error processing websocket message: %s", e)

            except websockets.exceptions.WebSocketException as e:
                _LOGGER.warning("Websocket connection error: %s", e)
                await asyncio.sleep(5)
            except Exception as e:
                _LOGGER.warning("Websocket error: %s", e)
                await asyncio.sleep(5)
    
    def _is_relevant_update(self, data: dict) -> bool:
        """Prüfe ob die WS-Nachricht für den Scheduler relevant ist."""
        if not isinstance(data, dict):
            return False
        
        # EVCC sendet Updates mit verschiedenen Strukturen
        # Relevante Events: vehicle changes, plan changes, active vehicle changes
        
        # Bei vollständigem State-Update (enthält "vehicles")
        if "vehicles" in data:
            return True
        
        # Bei Event-basiertem Update
        event_type = data.get("event") or data.get("type")
        if event_type in ("vehicle", "plan", "activeVehicle", "state"):
            return True
        
        # Bei Path-Updates (EVCC nutzt manchmal path-basierte Updates)
        path = data.get("path", "")
        if "vehicle" in path or "plan" in path or "active" in path.lower():
            return True
        
        return False
