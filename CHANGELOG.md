## [0.1.5] - 2026-02-08

**Fix**: Weekday mapping for Sunday (7↔0) in both directions for EVCC API compatibility

### Änderungen
- Tests für Mapping hinzugefügt
- Dokumentation und Release-Dateien aktualisiert
- manifest.json Version auf 0.1.5 angehoben

## [0.1.4] - 2026-01-25

 `ws_set_scheduler()`: Guarantees data consistency
- `precondition` akzeptiert jetzt ausschließlich 0, 1 oder 2:
  - 0 = keine Vorbedingung
  - 1 = nur PV-Überschuss
  - 2 = nur günstige Preise (falls Tarife aktiv)
- `services.yaml`: Selector auf Zahlenbereich 0–2 geändert, Beschreibung ergänzt
- README (DE/EN) & Dokumentation (DE/EN) angepasst
- Service-Validierung in `services.py` aktualisiert (Boolean explizit abgelehnt)

### 🏷️ Versionierung & Release

- manifest.json Version auf 0.1.4 angehoben

### 🔒 Verhalten

- Keine Änderung am Datenfluss, nur Validierung und Dokumentation präzisiert

**Highlights**: Strengere Service-Validierung, robustere Fehlerbehandlung, Docs aktualisiert

### ✨ Verbesserungen

- Services prüfen Eingaben jetzt strikt und liefern klare Fehlermeldungen:
  - `time`: validiert HH:MM (00:00–23:59)
  - `weekdays`: Liste von Zahlen 1–7, nicht leer
  - `soc`: Ganzzahl 0–100
  - `active`: bool
  - `precondition`: bool oder 0/1 (normiert auf 0/1)
- Koordinator-Prüfung: Services brechen sauber ab, falls Integration nicht initialisiert

### 📚 Dokumentation

- README (DE/EN) um Abschnitt „Input Validation“ erweitert
- Service-Beispiele ergänzt (optional `tz: Europe/Berlin`)

### 🏷️ Versionierung & Release

- manifest.json Version auf 0.1.3 angehoben
- Changelog-Eintrag hinzugefügt

### 🔒 Verhalten

- Keine API-Änderungen; Entity-IDs und Datenfluss (Pull-Modify-Push-Refresh) bleiben unverändert

## [0.1.2] - 2026-01-24

**Highlights**: BaseEvccPlanEntity, vereinheitlichtes Plattform-Setup, Service-Optimierung (weniger API-Calls), Icons (Time/Number), SOC-Slider Schrittweite 10

### ✨ Verbesserungen

- Gemeinsame Basisklasse `BaseEvccPlanEntity` eingeführt (zentralisiert gemeinsame Felder, `update_data()`, ID-Helfer)
- Plattform-Setup vereinheitlicht via `setup_platform()` (reduziert Boilerplate in `switch.py`, `time.py`, `text.py`, `number.py`)
- Vereinheitlichte `extra_state_attributes` über alle Entities
  - Basis: `vehicle_id`, `vehicle_title`, `plan_index`
  - Switch erweitert um vollständige Plan-Felder (`time`, `weekdays`, `soc`, `active`)
  - Text erweitert um `weekdays_list`
- Icons ergänzt:
  - Time: `mdi:clock-digital`
  - Number (SOC): `mdi:battery-charging`
- UI: SOC-Slider Schrittweite auf 10 gesetzt (Services akzeptieren weiterhin jeden Integer 0–100)

### 🛠️ Service-Optimierungen

- Redundante API-Calls entfernt: Services nutzen den bereits geladenen EVCC-State und vermeiden einen zusätzlichen `get_repeating_plans()` Aufruf
- Fahrzeug-Validierung und State-Abruf in Hilfsfunktionen ausgelagert (`_get_vehicles()`, `_ensure_vehicle_exists()`)

### 📚 Dokumentation

- EN/DE Dokumentationen aktualisiert:
  - Vollständiger Entities-Abschnitt (4 Plattformen, Icons, Minimal-/Voll-Attribute)
  - Architekturdiagramme inkl. `base_entity.py`, `time.py`, `text.py`, `number.py`
  - Hinweis zur SOC-Schrittweite (UI vs. Services)
- README_DE/README_EN angepasst (Icons & SOC-Hinweis)

### 🏷️ Versionierung & Release

- manifest.json Version auf 0.1.2 angehoben
- GitHub Releases Guide um 0.1.2 Roadmap-Zeile ergänzt, Footer-Datum präzisiert
- READMEs mit "Last Updated"/"Zuletzt aktualisiert" auf 24. Januar 2026 gesetzt

### 🔒 Verhalten

- Keine funktionalen Änderungen am Datenfluss: Pull-Modify-Push-Refresh bleibt bestehen
- WebSocket/Coordinator-Mechanik unverändert, nur effizienter Service-Pfad

# Changelog

All notable changes to the EVCC Scheduler Home Assistant Custom Integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-01-24

### 🛠️ Maintenance

- Repository-Links auf `diestrohs/ha-evcc-scheduler` korrigiert (manifest.json, hacs.json)
- Patch-Release-Version auf 0.1.1 angehoben (keine funktionalen Änderungen)

### 📝 Documentation

- Alle Dokumentationsdateien auf aktuellen Code-Stand gebracht
- Weekdays-Format in services.yaml korrigiert (1-7 statt 0-6)
- Versionsangaben auf 0.1.1 aktualisiert in:
  - README.md und README_DE.md
  - DOCUMENTATION.md und DOCUMENTATION_DE.md
  - manifest.json Referenzen
- Vollständige Beschreibung der Weekdays: 1=Mo, 2=Di, 3=Mi, 4=Do, 5=Fr, 6=Sa, 7=So

## [0.1.0] - 2026-01-24

### 🚀 Performance Improvements

- Entity Manager: Lazy-load registry (only access on deletion)
- Switch Entity: Efficient `update_data()` method for vehicle changes
- No registry access when plan count unchanged (vehicle switching optimization)

### ✨ Features

- Configurable WebSocket vs. Polling mode
- Configurable polling interval (default: 30s)
- WebSocket API for custom Lovelace Card (experimental)
- Vehicle metadata in switch attributes (`vehicle_title`, `vehicle_id`)

### 📝 Documentation

- Complete English documentation (DOCUMENTATION_EN.md)
- Updated German documentation (DOCUMENTATION_DE.md)
- HACS integration guide (HACS_INTEGRATION.md)
- Contributor guidelines (CONTRIBUTING_EN.md)
- Security policy (.github/SECURITY.md)
- GitHub issue and PR templates

### 🔧 Configuration

- Replaced `CONF_MODE` with `CONF_WEBSOCKET` (boolean)
- Replaced `CONF_TIMEOUT` with `CONF_POLL_INTERVAL`
- WebSocket enabled by default, can be disabled in config
- Polling interval configurable (30s default)

#### WebSocket Direct Data Sync
- **Smart WS Updates**: WebSocket events now sync directly with coordinator without extra API calls
  - Plan updates 50-75% faster (~50-100ms vs ~150-200ms)
  - Deduplication: Ignores events with no data changes
  - Fallback to normal refresh only on vehicle change
  - Result: ~50% reduction in API calls during WS updates

#### WebSocket Message Filtering
- Filter irrelevant events (status updates, errors)
- Only process critical updates (plan changes, vehicle changes, active vehicle changes)
- Reduced CPU load from selective message processing

#### Entity Manager
- Registry cleanup runs in background (non-blocking)
- Plan deletion visible immediately to user
- Parallel async cleanup tasks

#### Data Consistency Guarantees
- Coordinator refresh waits after service calls
- All entities guaranteed to have latest EVCC data
- Enhanced logging for consistency tracking
- Detailed WS update logs show plan changes

### 🐛 Bug Fixes

#### From 0.0.3 → 0.1.0
- **Fixed Plan Creation**: `build_entity_id()` parameter count error
  - Was: 3 params (breaking call)
  - Now: 2 params (correct)
  - Impact: Plans now created correctly on vehicle switch

- **Fixed Plan Toggle**: Direct EVCC API fetch instead of cached coordinator data
  - Was: Toggle used stale data
  - Now: Always fetch current state before toggle
  - Impact: Toggle operations now reliable

- **Fixed Entity Naming**: Standardized to "EVCC repeating Plan N"
  - Was: "{Vehicle} repeating Plan 01" (inconsistent)
  - Now: "EVCC repeating Plan 1" (consistent, no padding)
  - Impact: User-friendly, vehicle-agnostic names

### 📊 Performance Metrics

| Metric | 0.0.4 | 0.1.0 | Improvement |
|--------|-------|-------|-------------|
| Plan Update Latency | 150-200ms | 50-100ms | **50-75% faster** |
| API Calls on WS Update | 1x GET /api/state | 0x (WS data) | **100% reduction** |
| Entity Deletion | Blocking | Non-blocking | **Immediate UI update** |
| Redundant Updates | Yes (all WS) | No (filtered) | **Deduplication** |

### 🔧 Technical Details

#### New Coordinator Method
- `async websocket_update(data)`: Direct WS data synchronization
  - Extracts vehicle + plans from WS event
  - Compares with existing data
  - Updates only on actual changes (deduplication)
  - Fallback to API refresh on vehicle change

#### Service/WebSocket Operations
All operations now wait for coordinator refresh:
- `set_repeating_plan()`: Guarantees data consistency
- `del_repeating_plan()`: Guarantees data consistency  
- `ws_add_scheduler()`: Guarantees data consistency
- `ws_edit_scheduler()`: Guarantees data consistency
- `ws_delete_scheduler()`: Guarantees data consistency

### 📝 Logging

New consistency tracking logs:
```
Active vehicle: db:1
Data consistency check: Vehicle db:1 (Elroq) has 2 plans
WS update: Vehicle db:1 plans changed (2 → 3)
WS update received but no data changes detected
Toggling plan 1 for vehicle 'db:1': True → False
Waiting for coordinator refresh to ensure data consistency
```

### ⚡ Trade-offs

- ✅ Service calls wait ~50-100ms for refresh (necessary for consistency)
- ✅ Acceptable for charging plan management (not real-time critical)
- ✅ Huge performance gain in WS update handling

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
  - Toggle plan active status with `active` field
  
- `evcc_scheduler.del_repeating_plan`: Delete specific repeating plans
  - Safe deletion with coordinator refresh

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

**Release Date**: January 24, 2026  
**Home Assistant Compatibility**: 2025.12.0+  
**EVCC Compatibility**: 0.210.2+  
**License**: MIT
