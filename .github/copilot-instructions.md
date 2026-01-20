# EVCC Scheduler AI Instructions

## Architecture Overview

**EVCC Scheduler** is a Home Assistant custom component for managing EV charging schedules via the EVCC API. The component follows Home Assistant's standard integration pattern:

```
config_flow.py ──→ __init__.py ──→ coordinator.py ──→ api.py (HTTP)
                      ↓
              websocket_client.py (WS reconnection loop)
                      ↓
              entity_manager.py ←→ switch.py (plan entities)
                      ↓
              services.py (CRUD operations)
```

**Core Components**:
- `api.py`: Async aiohttp REST client for EVCC `/api/state` and `/api/vehicles/{id}/plan/repeating`
- `coordinator.py`: DataUpdateCoordinator with 30s polling interval; maintains `id_map` (vehicle_id → title)
- `websocket_client.py`: Persistent WS connection with 5s reconnect backoff; triggers coordinator refresh on message
- `switch.py`: `EvccPlanSwitch` entity per repeating plan; toggles call `_toggle_active()` → full plan sync pattern
- `entity_manager.py`: Handles dynamic entity lifecycle (create/update/delete) via `sync()` callback
- `services.py`: Registers `set_repeating_plan` and `del_repeating_plan` services
- `mapping.py`: Plan extraction (`extract_plans()`) and safe ID generation (`build_entity_id()`)

## Critical Data Flow Pattern

**The "Pull-Modify-Push-Refresh" Cycle**:
1. User toggles switch in HA → `async_turn_on()/async_turn_off()` → `_toggle_active(active)`
2. `_toggle_active()` calls `api.get_repeating_plans(vehicle_id)` → fetches ALL plans (0-based array)
3. Modifies `plans[self.index - 1]["active"] = active` (note: UI is 1-based, array is 0-based)
4. Pushes back: `api.set_repeating_plans(vehicle_id, plans)` with entire array
5. Triggers: `coordinator.async_request_refresh()` → coordinator fetches new state via `_async_update_data()`
6. Coordinator extracts plans via `mapping.extract_plans()` → entity manager's `sync()` callback
7. Entity manager compares current entities with desired state (via `build_entity_id()`) → updates/adds/removes entities

**Why this pattern?** EVCC API requires sending entire plan array on updates; coordinator refresh ensures all entities stay synchronized and prevents race conditions.

## Key Patterns & Conventions

### Plan Indexing: 1-Based Display, 0-Based Array
- EVCC stores plans as arrays: `[plan0, plan1, plan2]` (0-indexed)
- HA entity names use 1-based indexing: `plan_01`, `plan_02`, `plan_03` (user-friendly)
- In `switch.py`: `self.index` is 1-based display → access as `plans[self.index - 1]` in API calls
- In `entity_manager.py`: `enumerate(plans, start=1)` ensures 1-based indexing for entity IDs

### Vehicle ID Sanitization
- EVCC vehicle IDs may contain special chars: `vehicle:123`, `car-001`, etc.
- `mapping.build_entity_id()` sanitizes: `.lower().replace(":", "_")` → safe for HA entity registries
- Coordinator maintains `id_map` (raw ID → display title) for lookup

### Coordinator Data Structure
Coordinator's `_async_update_data()` returns:
```python
{
    "vehicles": {
        "vehicle:123": {
            "title": "Tesla",
            "repeatingPlans": [
                {"time": "07:00", "weekdays": [1,2,3], "soc": 80, "active": True},
                {...}
            ]
        }
    }
}
```
Entity manager expects this exact structure; if API response differs, update `mapping.extract_plans()`.

### WebSocket vs. Polling Strategy
- WebSocket (preferred): Configured in `config_flow.py` (default `MODE_WEBSOCKET`); connects on setup, triggers coordinator refresh on message
- Fallback polling: Coordinator's 30s interval catches missed updates if WS disconnects
- WS reconnect loop: 5s backoff in `websocket_client.py` `_run()`; doesn't block main HA event loop
- **Recommendation**: Always use WS if EVCC supports it; polling adds latency

### Config Flow & Entry Storage
- `config_flow.py` collects: `host` (required), `port` (default 7070), `token` (optional), `ssl`, `timeout`, `mode`
- Entry data stored in `hass.data[DOMAIN][entry.entry_id] = coordinator`
- Coordinator also stored in coordinator object: `coordinator.ws = ws` (for cleanup on unload)

## Common Implementation Patterns

### Adding a New Plan Property
1. Ensure EVCC API returns it in `/api/vehicles/{id}/plan/repeating` response
2. Property automatically included in entity's `extra_state_attributes()` (returns `self.plan.copy()`)
3. If service needs to modify it: add validation in `services.py` `set_repeating_plan()` → extract from `call.data`

### Fixing Entity Sync Issues
- **Problem**: Entities not updating or disappearing
- **Debug steps**:
  1. Check `coordinator.data` structure via Home Assistant logs (enable DEBUG for `evcc_scheduler`)
  2. Verify `mapping.extract_plans()` correctly parses EVCC response
  3. Check `entity_manager.sync()`: `build_entity_id()` output must match registry lookup
  4. If plan count changes: ensure `enumerate(plans, start=1)` is used for 1-based indexing

### Handling Plan Index Mismatches
- **Symptom**: Toggling plan 2 affects plan 1
- **Root cause**: Index off-by-one error in `_toggle_active()` or `entity_manager.sync()`
- **Fix**: Always convert UI index (1-based) to array index (0-based): `plans[idx - 1]`

### API Error Handling
- **GET failures**: `api.py` raises via `resp.raise_for_status()` → propagates to caller
- **POST failures**: Similar exception path; coordinator refresh will retry in 30s
- **Timeout**: Configured via `CONF_TIMEOUT` (default 10s); adjust in config_flow if EVCC is slow
- **Common errors**:
  - `vehicle_id` format incorrect (e.g., missing colon sanitization)
  - Port mismatch (EVCC default is 7070; check manifest.json and config_flow.py)
  - Token authentication if EVCC has auth enabled

## Testing & Debugging Approach

### Without Test Suite
- **Manual testing**: Use Home Assistant UI → Developer Tools → Services
- **Service test**: Call `evcc_scheduler.set_repeating_plan` with valid `vehicle_id`, `plan_index`, and plan data
- **Log inspection**: Set `evcc_scheduler` logger to DEBUG in `configuration.yaml`:
  ```yaml
  logger:
    logs:
      evcc_scheduler: debug
  ```
- **API testing**: Use curl to verify EVCC endpoint:
  ```bash
  curl http://localhost:7070/api/state | jq '.vehicles'
  curl http://localhost:7070/api/vehicles/vehicle:123/plan/repeating
  ```

### WebSocket Debugging
- Check `websocket_client.py` logs for connection/reconnection messages
- Verify WS endpoint format: `ws://host:port/ws` (not `http://`)
- Test: `wscat -c ws://localhost:7070/ws` or similar WebSocket client

### Entity Registry Issues
- Check Home Assistant entity registry: Settings → Devices & Services → Entities
- If entities don't appear: Check `async_add_entities()` call in `switch.py` setup
- If duplicates appear: Check `entity_manager.sync()` for unique_id collisions

## File Dependency Map

```
__init__.py
  ├─→ coordinator.py (setup coordinator, store in hass.data)
  ├─→ api.py (pass to coordinator)
  ├─→ websocket_client.py (setup WS with coordinator callback)
  └─→ services.py (register services once)

coordinator.py
  ├─→ api.py (fetch state)
  └─→ mapping.py (extract_plans, extract title mapping)

switch.py
  ├─→ coordinator (toggle calls → api → refresh)
  ├─→ entity_manager.py (sync callback)
  └─→ mapping.py (build_entity_id for sync)

entity_manager.py
  ├─→ mapping.py (build_entity_id)
  └─→ hass.helpers.entity_registry (async_get_registry)

services.py
  ├─→ api.py (get/set plans)
  └─→ hass.data[DOMAIN] (coordinator lookup)

config_flow.py
  └─→ const.py (DOMAIN, ports, modes)
```

## Quick Reference: What to Edit When

| Need | Edit File(s) |
|------|---------------|
| Add/change EVCC endpoint | `api.py` |
| Change poll interval or coordinator behavior | `coordinator.py` |
| Add/modify switch behavior or plan properties | `switch.py` + `mapping.py` |
| Add new service or modify call signature | `services.py` |
| Change entity ID format or naming | `mapping.py` + `entity_manager.py` |
| Add config options (host, port, token, etc.) | `config_flow.py` + `const.py` |
| Modify WS reconnect logic | `websocket_client.py` |
| Debug entity lifecycle issues | `entity_manager.py` |
