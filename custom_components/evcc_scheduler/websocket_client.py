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
        """Prüfe ob die WS-Nachricht für den Scheduler relevant ist.
        
        Filtert nur KRITISCHE Updates heraus, um unnötige Coordinator-Refreshes zu vermeiden.
        Ignoriert General-Updates (wie Fehler, Netzwerk-Status, etc.).
        """
        if not isinstance(data, dict):
            return False
        
        # KRITISCH: Vollständiges State-Update (enthält vehicles + loadpoints)
        # Dies ist selten, aber wenn EVCC neuen Gesamtstate sendet, müssen wir updaten
        if "vehicles" in data and "loadpoints" in data:
            _LOGGER.debug("Full state update detected from WS")
            return True
        
        # KRITISCH: Vehicle/Plan-spezifische Updates (path-basiert)
        path = data.get("path", "")
        
        # Plan-Änderungen sind DRINGEND
        if "repeatingPlans" in path:
            _LOGGER.debug("Plan change detected in WS path: %s", path)
            return True
        
        # Vehicle-Name/Title-Änderungen sind WICHTIG (Fahrzeugwechsel)
        if "/vehicles/" in path and ("title" in path or "name" in path):
            _LOGGER.debug("Vehicle name/title change detected: %s", path)
            return True
        
        # Aktives Fahrzeug in Ladestation geändert
        if "vehicleName" in path or "activeVehicle" in path:
            _LOGGER.debug("Active vehicle changed: %s", path)
            return True
        
        # Alles andere ignorieren (Status-Updates, Netzwerk-Infos, etc.)
        return False
