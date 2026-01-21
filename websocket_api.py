"""WebSocket API für EVCC Scheduler Custom-Card (experimentell/ungestestet)."""
import asyncio
import json
import logging
from typing import Any, Callable, Dict, Set, Optional

from homeassistant.core import HomeAssistant
from homeassistant.components import websocket_api

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class EvccWebSocketAPI:
    """WebSocket API Server für EVCC Scheduler Card"""

    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.clients: Set[Any] = set()
        self._handlers: Dict[str, Callable] = {}

    def register_handler(self, msg_type: str, handler: Callable) -> None:
        """Registriere einen Message-Handler"""
        self._handlers[msg_type] = handler

    async def handle_client(self, ws: Any) -> None:
        """Handle WebSocket client connection"""
        self.clients.add(ws)
        _LOGGER.debug("WebSocket client connected. Total clients: %d", len(self.clients))

        try:
            async for msg in ws:
                try:
                    data = json.loads(msg)
                    await self._handle_message(data, ws)
                except json.JSONDecodeError:
                    _LOGGER.warning("Invalid JSON received: %s", msg)
                except Exception as e:
                    _LOGGER.error("Error handling message: %s", e)
        except asyncio.CancelledError:
            pass
        finally:
            self.clients.discard(ws)
            _LOGGER.debug("WebSocket client disconnected. Total clients: %d", len(self.clients))

    async def _handle_message(self, data: Dict[str, Any], ws: Any) -> None:
        """Verarbeite eine WebSocket-Nachricht"""
        msg_type = data.get("type")
        
        if msg_type not in self._handlers:
            _LOGGER.warning("Unknown message type: %s", msg_type)
            return

        handler = self._handlers[msg_type]
        response = await handler(data)
        
        if response:
            await ws.send(json.dumps(response))

    async def broadcast(self, data: Dict[str, Any]) -> None:
        """Sende eine Nachricht an alle verbundenen Clients"""
        if not self.clients:
            return

        msg = json.dumps(data)
        
        # Entferne disconnected clients
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(msg)
            except Exception as e:
                _LOGGER.debug("Error sending to client: %s", e)
                disconnected.add(client)
        
        self.clients -= disconnected

    async def close_all(self) -> None:
        """Schließe alle Clients"""
        for client in list(self.clients):
            try:
                await client.close()
            except Exception as e:
                _LOGGER.debug("Error closing client: %s", e)
        self.clients.clear()


# --- Home Assistant WebSocket API Commands ---


def _get_coordinator(hass: HomeAssistant):
    domain_data = hass.data.get(DOMAIN)
    if not domain_data:
        raise ValueError("Coordinator not initialized")
    # Single entry supported → nimm den ersten
    return next(iter(domain_data.values()))


def _convert_weekdays_to_user(weekdays: Optional[list]) -> Optional[list]:
    """Konvertiere Wochentage von EVCC-Format (0-6) zu User-Format (1-7).
    
    EVCC: 0=Sonntag, 1=Montag, 2=Dienstag, 3=Mittwoch, 4=Donnerstag, 5=Freitag, 6=Samstag
    User: 1=Montag, 2=Dienstag, 3=Mittwoch, 4=Donnerstag, 5=Freitag, 6=Samstag, 7=Sonntag
    """
    if not weekdays:
        return weekdays
    converted = []
    for day in weekdays:
        if isinstance(day, int):
            # 0 (Sonntag) → 7, sonst unverändert
            converted.append(7 if day == 0 else day)
        else:
            converted.append(day)
    return converted


def _convert_weekdays_to_api(weekdays: Optional[list]) -> Optional[list]:
    """Konvertiere Wochentage von User-Format (1-7) zu EVCC-Format (0-6).
    
    User: 1=Montag, 2=Dienstag, 3=Mittwoch, 4=Donnerstag, 5=Freitag, 6=Samstag, 7=Sonntag
    EVCC: 0=Sonntag, 1=Montag, 2=Dienstag, 3=Mittwoch, 4=Donnerstag, 5=Freitag, 6=Samstag
    """
    if not weekdays:
        return weekdays
    converted = []
    for day in weekdays:
        if isinstance(day, int):
            # 7 (Sonntag) → 0, sonst unverändert
            converted.append(0 if day == 7 else day)
        else:
            converted.append(day)
    return converted


@websocket_api.websocket_command({"type": "scheduler/get"})
@websocket_api.async_response
async def ws_get_scheduler(hass: HomeAssistant, connection, msg) -> None:
    """Gib aktuelle repeatingPlans für das aktiv ausgewählte EVCC-Fahrzeug zurück."""
    try:
        coordinator = _get_coordinator(hass)
        data = coordinator.data or {}
        vehicles = data.get("vehicles", {})
        
        # Konvertiere Wochentage für User (EVCC 0-6 → User 1-7)
        result_vehicles = {}
        for vid, vdata in vehicles.items():
            result_vehicles[vid] = {
                "title": vdata.get("title"),
                "repeatingPlans": [
                    {**plan, "weekdays": _convert_weekdays_to_user(plan.get("weekdays"))}
                    for plan in vdata.get("repeatingPlans", [])
                ]
            }
        
        connection.send_result(msg["id"], {"vehicles": result_vehicles})
    except Exception as err:
        connection.send_error(msg["id"], "failed", str(err))


@websocket_api.websocket_command({"type": "scheduler/add"})
@websocket_api.async_response
async def ws_add_scheduler(hass: HomeAssistant, connection, msg) -> None:
    """Füge einen repeatingPlan hinzu (weekdays: 1=Montag, 7=Sonntag)."""
    try:
        coordinator = _get_coordinator(hass)
        data = coordinator.data or {}
        vehicles = data.get("vehicles", {})
        
        # Hole die vehicle_id des aktuell geladenen Fahrzeugs
        if not vehicles:
            raise ValueError("Kein Fahrzeug geladen")
        
        vehicle_id = next(iter(vehicles.keys()))
        plans = await coordinator.api.get_repeating_plans(vehicle_id)

        new_plan = {}
        for key in ("time", "soc", "active"):
            if key in msg:
                new_plan[key] = msg[key]
        # Konvertiere Wochentage: User 1-7 → EVCC 0-6
        if "weekdays" in msg:
            new_plan["weekdays"] = _convert_weekdays_to_api(msg["weekdays"])

        plans.append(new_plan)
        await coordinator.api.set_repeating_plans(vehicle_id, plans)
        await coordinator.async_request_refresh()

        # Konvertiere Pläne zurück zu User-Format für Response/Broadcast
        user_plans = [
            {**plan, "weekdays": _convert_weekdays_to_user(plan.get("weekdays"))}
            for plan in plans
        ]
        api = hass.data.get("evcc_scheduler_ws_api")
        if api:
            await api.broadcast({"type": "plans_updated", "vehicle_id": vehicle_id, "plans": user_plans})

        connection.send_result(msg["id"], {"vehicle_id": vehicle_id, "plans": user_plans})
    except Exception as err:
        connection.send_error(msg["id"], "failed", str(err))


@websocket_api.websocket_command({"type": "scheduler/edit", "plan_index": int})
@websocket_api.async_response
async def ws_edit_scheduler(hass: HomeAssistant, connection, msg) -> None:
    """Bearbeite einen repeatingPlan (plan_index: 1-basiert, weekdays: 1=Montag, 7=Sonntag)."""
    try:
        coordinator = _get_coordinator(hass)
        data = coordinator.data or {}
        vehicles = data.get("vehicles", {})
        
        # Hole die vehicle_id des aktuell geladenen Fahrzeugs
        if not vehicles:
            raise ValueError("Kein Fahrzeug geladen")
        
        vehicle_id = next(iter(vehicles.keys()))
        plan_index = msg["plan_index"] - 1  # Konvertiere 1-basiert zu 0-basiert

        plans = await coordinator.api.get_repeating_plans(vehicle_id)
        if not (0 <= plan_index < len(plans)):
            raise IndexError("plan_index out of range")

        for key in ("time", "soc", "active"):
            if key in msg:
                plans[plan_index][key] = msg[key]
        # Konvertiere Wochentage: User 1-7 → EVCC 0-6
        if "weekdays" in msg:
            plans[plan_index]["weekdays"] = _convert_weekdays_to_api(msg["weekdays"])

        await coordinator.api.set_repeating_plans(vehicle_id, plans)
        await coordinator.async_request_refresh()

        # Konvertiere Pläne zurück zu User-Format für Response/Broadcast
        user_plans = [
            {**plan, "weekdays": _convert_weekdays_to_user(plan.get("weekdays"))}
            for plan in plans
        ]
        api = hass.data.get("evcc_scheduler_ws_api")
        if api:
            await api.broadcast({"type": "plans_updated", "vehicle_id": vehicle_id, "plans": user_plans})

        connection.send_result(msg["id"], {"vehicle_id": vehicle_id, "plans": user_plans})
    except Exception as err:
        connection.send_error(msg["id"], "failed", str(err))


@websocket_api.websocket_command({"type": "scheduler/deleate", "plan_index": int})
@websocket_api.async_response
async def ws_delete_scheduler(hass: HomeAssistant, connection, msg) -> None:
    """Lösche einen repeatingPlan (plan_index: 1-basiert)."""
    try:
        coordinator = _get_coordinator(hass)
        data = coordinator.data or {}
        vehicles = data.get("vehicles", {})
        
        # Hole die vehicle_id des aktuell geladenen Fahrzeugs
        if not vehicles:
            raise ValueError("Kein Fahrzeug geladen")
        
        vehicle_id = next(iter(vehicles.keys()))
        plan_index = msg["plan_index"] - 1  # Konvertiere 1-basiert zu 0-basiert

        plans = await coordinator.api.get_repeating_plans(vehicle_id)
        if not (0 <= plan_index < len(plans)):
            raise IndexError("plan_index out of range")

        plans.pop(plan_index)
        await coordinator.api.set_repeating_plans(vehicle_id, plans)
        await coordinator.async_request_refresh()

        # Konvertiere Pläne zurück zu User-Format für Response/Broadcast
        user_plans = [
            {**plan, "weekdays": _convert_weekdays_to_user(plan.get("weekdays"))}
            for plan in plans
        ]
        api = hass.data.get("evcc_scheduler_ws_api")
        if api:
            await api.broadcast({"type": "plans_updated", "vehicle_id": vehicle_id, "plans": user_plans})

        connection.send_result(msg["id"], {"vehicle_id": vehicle_id, "plans": user_plans})
    except Exception as err:
        connection.send_error(msg["id"], "failed", str(err))


def async_register_ws_commands(hass: HomeAssistant) -> None:
    """Registriere die HA-WS-Kommandos."""
    websocket_api.async_register_command(hass, ws_get_scheduler)
    websocket_api.async_register_command(hass, ws_add_scheduler)
    websocket_api.async_register_command(hass, ws_edit_scheduler)
    websocket_api.async_register_command(hass, ws_delete_scheduler)
