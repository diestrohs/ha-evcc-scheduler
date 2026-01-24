import asyncio
import json
import logging
import random
import re
import websockets

_LOGGER = logging.getLogger(__name__)

class EvccWebsocketClient:
    def __init__(self, host, port, coordinator_callback):
        self.url = f"ws://{host}:{port}/ws"
        self.coordinator_callback = coordinator_callback
        self._task = None
        self._consumer_task = None
        self._ws = None
        self._running = False
        self._message_queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._last_signature: str | None = None

        # Backoff-Konfiguration
        self._backoff_base = 1
        self._backoff_max = 60

    async def connect(self):
        if self._task and not self._task.done():
            _LOGGER.debug("Websocket client already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run())
        self._consumer_task = asyncio.create_task(self._consume_messages())

    async def disconnect(self):
        self._running = False
        if self._ws:
            try:
                await self._ws.close()
            except Exception as err:
                _LOGGER.debug("Error during websocket close: %s", err)

        for task in (self._task, self._consumer_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as err:
                    _LOGGER.debug("Error awaiting task cancel: %s", err)

        self._task = None
        self._consumer_task = None
        self._ws = None
        self._clear_queue()

    async def _run(self):
        backoff = self._backoff_base
        while self._running:
            try:
                async with websockets.connect(
                    self.url,
                    open_timeout=10,
                    ping_interval=30,
                    ping_timeout=10,
                    max_size=1_000_000,
                ) as ws:
                    self._ws = ws
                    _LOGGER.info("Connected to EVCC websocket at %s", self.url)
                    backoff = self._backoff_base  # Reset nach erfolgreichem Connect

                    async for msg in ws:
                        try:
                            data = json.loads(msg)
                            
                            # Filtere relevante Nachrichten für sofortiges Update
                            # EVCC sendet verschiedene Event-Typen
                            if self._is_relevant_update(data):
                                _LOGGER.debug("Relevant WS message received, triggering coordinator refresh")
                                signature = self._signature(data)
                                if signature == self._last_signature:
                                    _LOGGER.debug("Skipping duplicate WS message")
                                    continue
                                self._last_signature = signature

                                if not self._message_queue.full():
                                    await self._message_queue.put(data)
                                else:
                                    _LOGGER.warning("WS message queue full; dropping message")
                        except json.JSONDecodeError:
                            _LOGGER.debug("Non-JSON websocket message ignored")
                        except Exception as e:
                            _LOGGER.error("Error processing websocket message: %s", e)

            except websockets.exceptions.WebSocketException as e:
                _LOGGER.warning("Websocket connection error: %s", e)
                sleep_for = self._next_backoff(backoff)
                _LOGGER.debug("Backoff after WS error: %.2fs", sleep_for)
                await asyncio.sleep(sleep_for)
                backoff = min(backoff * 2, self._backoff_max)
            except asyncio.CancelledError:
                _LOGGER.debug("Websocket run task cancelled")
                break
            except Exception as e:
                _LOGGER.warning("Websocket error: %s", e)
                sleep_for = self._next_backoff(backoff)
                _LOGGER.debug("Backoff after WS error: %.2fs", sleep_for)
                await asyncio.sleep(sleep_for)
                backoff = min(backoff * 2, self._backoff_max)
            finally:
                self._ws = None
                self._last_signature = None

    async def _consume_messages(self):
        while self._running or not self._message_queue.empty():
            try:
                data = await self._message_queue.get()
                await self.coordinator_callback(data)
            except asyncio.CancelledError:
                _LOGGER.debug("Consumer task cancelled")
                break
            except Exception as err:
                _LOGGER.error("Error in consumer task: %s", err)
            finally:
                self._message_queue.task_done()

    def _clear_queue(self):
        while not self._message_queue.empty():
            try:
                self._message_queue.get_nowait()
                self._message_queue.task_done()
            except asyncio.QueueEmpty:
                break

    def _next_backoff(self, current: int) -> float:
        jitter = random.uniform(0, current)
        return min(current + jitter, self._backoff_max)
    
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

        # Plan-Änderungen sind DRINGEND (präziser Pfad-Check)
        if self._matches_plan_path(path):
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

    def _matches_plan_path(self, path: str) -> bool:
        if not path:
            return False
        pattern = r"^/api/vehicles/[^/]+/plan/repeating"
        return re.match(pattern, path) is not None

    def _signature(self, data: dict) -> str:
        try:
            return json.dumps(data, sort_keys=True)
        except Exception:
            return str(data)
