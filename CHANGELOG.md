# Changelog

All notable changes to the EVCC Scheduler Home Assistant Custom Integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.4] - 2026-01-21

### Added

#### Core Integration Features
- **DataUpdateCoordinator**: Implemented 30-second polling interval for automatic state refresh
- **WebSocket Support**: Real-time state updates from EVCC API via persistent WebSocket connection
  - Automatic reconnection with exponential backoff (5s base, max 60s)
  - Fallback to polling if WebSocket unavailable
  - Configurable via config flow (default: enabled)

#### Entity Management
- **Dynamic Entity Lifecycle**: Automatic creation, update, and deletion of plan entities
  - Entity Registry integration for cleanup on restart/unload
  - Safe entity ID generation with special character sanitization
  - Multi-vehicle support with entity migration on vehicle change

#### Services
- `evcc_scheduler.set_repeating_plan`: Create or update repeating charging plans
  - Validation: vehicle availability, plan index, required fields
  - Localized error messages (German)
  
- `evcc_scheduler.del_repeating_plan`: Delete specific repeating plans
  - Safe deletion with coordinator refresh
  
- `evcc_scheduler.toggle_plan_active`: Toggle active status of plans
  - Immediate feedback with state update

#### Switch Platform
- **EvccPlanSwitch**: Per-plan toggle entities
  - Attributes: time, weekdays, soc, active status
  - Bidirectional sync: UI toggle → API call → coordinator refresh
  - Full plan object in `extra_state_attributes`

#### WebSocket API for Custom Cards
- Custom Home Assistant WebSocket commands
- API Endpoints:
  - `scheduler/get`: Fetch current scheduler state
  - `scheduler/add`: Add new repeating plan
  - `scheduler/edit`: Modify existing plan
  - `scheduler/deleate`: Delete plan (matches EVCC typo)

#### Configuration
- **Config Flow**: User-friendly setup wizard
  - Host, Port (default 7070), SSL/TLS support
  - Token-based authentication (optional)
  - Timeout configuration (default 10s)
  - Connection mode selection (WebSocket/Polling)

#### HACS Integration
- Full HACS marketplace compatibility
- GitHub Actions CI/CD validation workflow
- Comprehensive documentation:
  - User guide (README.md)
  - Technical documentation (DOCUMENTATION.md - English)
  - German documentation (DOCUMENTATION_DE.md)
  - HACS-specific installation guide
  - Contribution guidelines
  - Code of Conduct (Contributor Covenant v2.1)
  - MIT License

### Technical Details

#### Architecture
```
config_flow.py ──→ __init__.py ──→ coordinator.py ──→ api.py
    ↓                  ↓
websocket_client.py    entity_manager.py ←→ switch.py
    ↓
websocket_api.py (Custom Card API)
```

#### Data Flow Pattern
1. User toggles plan switch in Home Assistant UI
2. Switch calls API to update plan status
3. API updates EVCC backend with full plan array
4. Coordinator triggers refresh (30s interval or WebSocket trigger)
5. Entity manager syncs entities with new state
6. UI updates with latest state

#### Vehicle Support
- Automatic vehicle detection from EVCC loadpoints
- Uses `loadpoints[].vehicleName` for vehicle identification
- Supports multiple vehicles with separate plan sets per vehicle
- Entity migration on vehicle change

#### Plan Indexing
- EVCC API: 0-based array indexing
- Home Assistant UI: 1-based entity names (plan_01, plan_02, etc.)
- Services: 1-based plan index (user-friendly)
- Automatic conversion in all layer transitions

### Dependencies
- **Python**: 3.11 or later
- **aiohttp**: >=3.8.0 (async HTTP client)
- **Home Assistant**: 2025.12.0 or later

### Known Limitations
- EVCC API token authentication is optional (some EVCC instances don't require it)
- WebSocket mode requires EVCC version 0.210.2 or later
- Plan modifications require full plan array submission to EVCC API

### Code Quality
- No circular dependencies
- Type hints throughout (ready for future mypy integration)
- Comprehensive error handling with user-friendly messages
- Localized German error messages
- Logging configured for DEBUG troubleshooting

### Testing
- Integration validation completed
- Entity management lifecycle tested
- Service registration and execution verified
- Multi-vehicle scenario tested
- WebSocket reconnection logic verified
- Entity Registry cleanup confirmed

### Files
- **Python Modules**: 11 (core integration)
- **Configuration**: manifest.json, hacs.json
- **Documentation**: 5 markdown files
- **Services**: services.yaml
- **Translations**: German (de.json), English (en.json)
- **CI/CD**: GitHub Actions workflow
- **License**: MIT License

---

## Future Roadmap

- [ ] Add tests with pytest coverage
- [ ] Implement type checking with mypy
- [ ] Add recurring plan templates
- [ ] Web UI dashboard for plan management
- [ ] Advanced scheduling (e.g., cost-based optimization)
- [ ] Integration with other Home Assistant energy automations
- [ ] Support for additional EVCC API features

---

**Release Date**: January 21, 2026  
**Home Assistant Compatibility**: 2025.12.0+  
**EVCC Compatibility**: 0.210.2+  
**License**: MIT
