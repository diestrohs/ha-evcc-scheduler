# EVCC Scheduler - Documentation

## Overview

**EVCC Scheduler** is a Home Assistant custom integration for managing recurring EV charging schedules via the EVCC API. The integration synchronizes vehicle selection with EVCC and provides centralized management of charging schedules with automatic cleanup of orphaned entities.

**License:** MIT  
**Repository:** [GitHub](https://github.com/diestrohs/ha-evcc-scheduler)  
**HACS:** ✅ Compatible & Available  
**Home Assistant:** 2025.12.0+  
**EVCC:** 0.210.2+

---

## Quick Start 🚀

### 1. Installation with HACS (1 Minute)

```
HACS → Integrations → ⋮ → Custom Repositories
→ https://github.com/diestrohs/ha-evcc-scheduler
→ Category: Integration
→ Search: EVCC Scheduler → Install
→ Restart Home Assistant ⭐ IMPORTANT
```

### 2. Configuration (2 Minutes)

```
Settings → Devices and Services → + Create Integration
→ Search: EVCC Scheduler
→ Host: 192.168.1.100 (EVCC IP)
→ Port: 7070 (Default)
→ Confirm ✅
```

### 3. Done! 🎉

- Entities are created automatically
- Services are available immediately
- WebSocket runs for real-time updates

---

## Features

### Core Features

- ✅ **Automatic Vehicle Selection**: Detects the selected vehicle in EVCC automatically
- ✅ **Dynamic Entity Management**: Creates/deletes entities based on current vehicle
- ✅ **Real-time Synchronization**: WebSocket updates with fallback to polling (30s)
- ✅ **Plan Management**: Services for creating, updating, deleting plans
- ✅ **Entity Registry Cleanup**: Removes orphaned entities on restart
- ✅ **Multi-Vehicle Support**: Handles multiple vehicles with automatic entity migration
- ✅ **Localized Messages**: German error messages with fallback to English
- ✅ **Type Hints**: Ready for future mypy integration
- ✅ **Home Assistant Standards**: Follows HA integration best practices

### Architecture

```
config_flow.py ──→ __init__.py ──→ coordinator.py ──→ api.py
    ↓                  ↓
websocket_client.py    entity_manager.py ←→ switch.py
    ↓                               ↓         time.py
websocket_api.py                    ↓         text.py
                                    ↓         number.py
```

---

## Installation

### Requirements

- Home Assistant 2025.12.0 or later
- EVCC 0.210.2 or later (WebSocket mode)
- Python 3.11 or later
- Network access to EVCC instance (local network recommended)

### Installation Steps

#### 1. With HACS (Recommended) 🎉

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the menu (top right) → "Custom Repositories"
4. Enter URL: `https://github.com/diestrohs/ha-evcc-scheduler`
5. Select **"Integration"** as category
6. Click "Create"
7. Search for "EVCC Scheduler" and click "Install"
8. **⚠️ Important**: Home Assistant restart required!

#### 2. Manual (Without HACS)

```bash
cd /config/custom_components
git clone https://github.com/diestrohs/ha-evcc-scheduler.git
# Restart Home Assistant
```

#### 3. Configure Integration

After installation and Home Assistant restart:

1. Go to **Settings** → **Devices and Services** → **Integrations**
2. Click **"+ Create Integration"**
3. Search for **"EVCC Scheduler"** and select it
4. Follow the configuration:
   - **Host**: IP or hostname of EVCC (e.g., `192.168.1.100`)
   - **Port**: EVCC API port (Default: `7070`)
   - **Token**: Optional, if EVCC requires token auth
   - **SSL**: Enable/disable based on EVCC setup
   - **Timeout**: HTTP timeout in seconds (Default: `10`)
   - **Communication Mode**: WebSocket (recommended) or Polling (Default: WebSocket)
   - **Polling Interval**: Seconds between updates (Default: `30`; only active in Polling mode)
   - **Custom Card WebSocket API (experimental/untested)**: Disabled by default; only enable if you need the Custom Card WS API

#### 4. Optional: Logging aktivieren

Füge folgende Zeilen in `configuration.yaml` ein für Debugging:

```yaml
logger:
  logs:
    evcc_scheduler: debug
    evcc_scheduler.api: debug
    evcc_scheduler.coordinator: debug
```

---

## Entities

Die Integration erstellt für jeden Ladeplan **vier verschiedene Entity-Typen**, um alle Plan-Eigenschaften einzeln bearbeitbar zu machen:

### Entity-Plattformen

#### 1. Switch - Ladeplan Aktiv/Inaktiv

Schaltet den Plan ein/aus.

**Entity-ID**: `switch.evcc_{fahrzeug}_repeating_plan_{index}_activ`

**Beispiel**: `switch.evcc_elroq_repeating_plan_1_activ`

**Funktionsweise**:
- ON: Plan wird ausgeführt
- OFF: Plan ist deaktiviert
- Toggle lädt alle Pläne, ändert nur `active`, speichert zurück

**Attribute**:
```yaml
vehicle_id: "db:1"
vehicle_title: "Elroq"
plan_index: 1
time: "07:00"
weekdays: [1, 2, 3, 4, 5]
soc: 80
active: true
```

#### 2. Time - Ladeplan Startzeit

Bearbeitet die Startzeit des Plans.

**Entity-ID**: `time.evcc_{fahrzeug}_repeating_plan_{index}_time`

**Beispiel**: `time.evcc_elroq_repeating_plan_1_time`

**Format**: HH:MM (24-Stunden)

**Attribute**:
```yaml
vehicle_id: "db:1"
vehicle_title: "Elroq"
plan_index: 1
```

#### 3. Text - Ladeplan Wochentage

Bearbeitet die Wochentage als komma-getrennte Liste.

**Entity-ID**: `text.evcc_{fahrzeug}_repeating_plan_{index}_weekdays`

**Beispiel**: `text.evcc_elroq_repeating_plan_1_weekdays`

**Format**: `"1,2,3,4,5"` (1=Montag, 7=Sonntag)

**Attribute**:
```yaml
vehicle_id: "db:1"
vehicle_title: "Elroq"
plan_index: 1
weekdays_list: [1, 2, 3, 4, 5]  # Array-Format für Automations
```

#### 4. Number - Ladeplan Zielladung

Bearbeitet die Zielladung in Prozent.

**Entity-ID**: `number.evcc_{fahrzeug}_repeating_plan_{index}_soc`

**Beispiel**: `number.evcc_elroq_repeating_plan_1_soc`

**Bereich**: 0-100%

**Attribute**:
```yaml
vehicle_id: "db:1"
vehicle_title: "Elroq"
plan_index: 1
unit_of_measurement: "%"
```

### Entity-Beispiel: Kompletter Ladeplan

Für einen Plan werden **4 Entities** erstellt:

```
Ladeplan 1 (Elroq):
├─ switch.evcc_elroq_repeating_plan_1_activ     → Anzeigename: "Ladeplan 1 Aktiv"
├─ time.evcc_elroq_repeating_plan_1_time        → Anzeigename: "Ladeplan 1 Startzeit"
├─ text.evcc_elroq_repeating_plan_1_weekdays    → Anzeigename: "Ladeplan 1 Wochentage"
└─ number.evcc_elroq_repeating_plan_1_soc       → Anzeigename: "Ladeplan 1 Zielladung"
```

**Übersetzung (Deutsch/Englisch)**:
- Entities zeigen automatisch deutsche oder englische Namen basierend auf HA-Sprache
- Gesteuert via `translations/de.json` und `translations/en.json`
- Translation Keys: `repeating_plan_activ`, `repeating_plan_time`, `repeating_plan_weekdays`, `repeating_plan_soc`

### Indexierung: 1-basiert, keine führenden Nullen

```
Plan 1 → evcc_elroq_repeating_plan_1_activ
Plan 2 → evcc_elroq_repeating_plan_2_time
Plan 3 → evcc_elroq_repeating_plan_3_weekdays
```

**Nicht**: ~~`evcc_elroq_repeating_plan_01_activ`~~ (alte Version)

---

## Architektur

```
Integration-Startup
        ↓
__init__.py (async_setup_entry)
    ├─→ api.py (REST-Client)
    ├─→ coordinator.py (DataUpdateCoordinator)
    │   └─→ Liest vehicleName aus loadpoints[]
    ├─→ websocket_client.py (WS-Verbindung)
    ├─→ websocket_api.py (WebSocket-API für UI)
    ├─→ services.py (Service-Registrierung)
    ├─→ switch.py (Plan Active/Inactive)
    ├─→ time.py (Plan Start Time)
    ├─→ text.py (Plan Weekdays)
    └─→ number.py (Plan Target SOC)
           └─→ entity_manager.py (Entity-Lifecycle mit suffix-Parameter)
                  └─→ mapping.py (ID-Generierung)
```

### Kernkomponenten

#### `api.py` - REST-Client
- **Aufgabe**: HTTP-Kommunikation mit EVCC
- **Methoden**:
  - `get_state()`: Holt kompletten EVCC-State
  - `get_repeating_plans(vehicle_id)`: Liste der Pläne eines Fahrzeugs
  - `set_repeating_plans(vehicle_id, plans)`: Speichert alle Pläne
- **Fehlerbehandlung**: `raise_for_status()` wirft Exceptions bei HTTP-Fehlern

#### `coordinator.py` - Data Update Coordinator
- **Aufgabe**: Zentrale Datenquelle, konfigurierbarer Polling-Intervall (Default: 30s)
- **Fahrzeugauswahl**: Iteriert `state["loadpoints"][]`, sucht `vehicleName`
- **Datenstruktur**:
  ```python
  {
    "vehicles": {
      "db:1": {
        "title": "Elroq",
        "repeatingPlans": [
          {"time": "07:00", "weekdays": [1,2,3], "soc": 80, "active": True},
          ...
        ]
      }
    },
    "id_map": {"db:1": "Elroq"}
  }
  ```
- **Verhalten bei Fahrzeugwechsel**: `wanted_ids` ändert sich → Entity Manager löscht alte Entities

#### `websocket_client.py` - WebSocket-Verbindung
- **Aufgabe**: Persistente WS-Verbindung zu EVCC
- **Reconnect-Logik**: 5s exponentieller Backoff bei Fehlern
- **Callback**: Triggert `coordinator.async_request_refresh()` bei neuen Nachrichten
- **Non-Blocking**: Läuft in separatem Task, blockiert nicht den HA Event Loop

#### `entity_manager.py` - Entity-Lifecycle
- **Aufgabe**: Synchronisiert Entities mit Coordinator-Daten (Multi-Plattform-Support)
- **Konstruktor**: `__init__(hass, async_add_entities, suffix="")` - suffix für verschiedene Entity-Typen
- **Sync-Prozess**:
  1. Vergleicht `wanted_ids` (aus Plänen) mit `current_ids` (in `self.entities`)
  2. Neue Entities: Erstellen und registrieren
  3. Bestehende Entities: Plan-Daten aktualisieren
  4. Entfernte Entities: Aus Dictionary entfernen + aus Registry löschen
- **Suffix-Handling**: Base-ID `evcc_{vehicle}_repeating_plan_{index}_activ` wird transformiert zu `_time`, `_weekdays`, `_soc`
- **Registry-Cleanup**: `async_remove()` bei jedem unload + bei async_unload_entry()

#### `switch.py` - Switch Platform (Active/Inactive Toggle)
- **Entität**: `EvccPlanSwitch` für jeden Plan
- **Entity-ID**: `evcc_{vehicle}_repeating_plan_{index}_activ` (1-basiert, z.B. `evcc_elroq_repeating_plan_1_activ`)
- **Translation Key**: `repeating_plan_activ` ("Ladeplan 1 Aktiv")
- **Icon**: Systemstandard
- **Attribute**: Alle Plan-Felder (`time`, `weekdays`, `soc`, `active`) + `vehicle_id`, `vehicle_title`
- **Toggle**: `async_turn_on/off()` → Lädt alle Pläne, ändert `active`, speichert zurück → `coordinator.async_request_refresh()`
- **1-basierte Indexierung**: UI zeigt Plan 1,2,3; intern `plans[self.index - 1]` (0-basiert)

#### `time.py` - Time Platform (Start Time Editor)
- **Entität**: `EvccPlanTime` für jeden Plan
- **Entity-ID**: `evcc_{vehicle}_repeating_plan_{index}_time` (z.B. `evcc_elroq_repeating_plan_1_time`)
- **Translation Key**: `repeating_plan_time` ("Ladeplan 1 Startzeit")
- **Icon**: `mdi:clock-digital`
- **Format**: HH:MM (24-Stunden-Format)
- **Attribute**: `vehicle_id`, `vehicle_title`, `plan_index`
- **Update**: `async_set_value()` → Validiert Format → API-Update → Coordinator-Refresh

#### `text.py` - Text Platform (Weekdays Editor)
- **Entität**: `EvccPlanWeekdays` für jeden Plan
- **Entity-ID**: `evcc_{vehicle}_repeating_plan_{index}_weekdays` (z.B. `evcc_elroq_repeating_plan_1_weekdays`)
- **Translation Key**: `repeating_plan_weekdays` ("Ladeplan 1 Wochentage")
- **Format**: Komma-getrennt "1,2,3,4,5" (1=Montag, 7=Sonntag)
- **Attribute**: `vehicle_id`, `vehicle_title`, `plan_index`, `weekdays_list` (Array-Format)
- **Validierung**: Prüft 1-7 Bereich, filtert Duplikate
- **Update**: `async_set_value()` → Parse "1,2,3" zu [1,2,3] → API-Update → Refresh

#### `number.py` - Number Platform (Target SOC Editor)
- **Entität**: `EvccPlanSoc` für jeden Plan
- **Entity-ID**: `evcc_{vehicle}_repeating_plan_{index}_soc` (z.B. `evcc_elroq_repeating_plan_1_soc`)
- **Translation Key**: `repeating_plan_soc` ("Ladeplan 1 Zielladung")
- **Icon**: `mdi:battery-charging`
- **Bereich**: 0-100% (Slider)
- **Einheit**: "%"
- **Attribute**: `vehicle_id`, `vehicle_title`, `plan_index`
- **Update**: `async_set_native_value()` → Validiert 0-100 → API-Update → Refresh
 - **Hinweis**: UI-Slider nutzt Schrittweite 10; Services können jeden Integer 0–100 setzen.

#### `services.py` - Service-Registrierung
- **Services**:
  - `evcc_scheduler.set_repeating_plan`
  - `evcc_scheduler.del_repeating_plan`
- **Validierung**: Prüft Fahrzeug-ID, Verfügbarkeit, Plan-Index
- **Fehlerbehandlung**: `ServiceValidationError` mit aussagekräftigen Meldungen
 - **Precondition**: Enum-Wert 0/1/2
    - `0`: keine Vorbedingung
    - `1`: nur bei PV-Überschuss
    - `2`: nur bei günstigen Preisen (falls Tarife aktiv)

#### `mapping.py` - Hilfsfunktionen
- `extract_plans()`: Konvertiert EVCC-State zu vehicles-Dict
- `build_entity_id(vehicle_id, index, title)`: Generiert Base-Entity-ID (mit `_activ` Suffix)
  - Format: `evcc_{fahrzeug}_repeating_plan_{index}_activ`
  - Index: 1-basiert OHNE führende Nullen (Plan 1, nicht Plan 01)
  - Beispiel: `build_entity_id("db:1", 1, "Elroq")` → `"evcc_elroq_repeating_plan_1_activ"`
  - Sanitization: `.lower().replace(":", "_")` für EVCC-IDs
- **Nutzung in Plattformen**: Suffix wird ausgetauscht: `base_id.replace("_activ", "_time")`, etc.

#### `websocket_api.py` - WebSocket-API für Custom Card
- **Aufgabe**: Ermöglicht Custom Lovelace Card, Daten zu holen
- **Commands**:
  - `type: "scheduler/get"`: Holt Fahrzeug + Pläne
  - `type: "scheduler/add"`: Neuen Plan anlegen
  - `type: "scheduler/edit"`: Plan bearbeiten
  - `type: "scheduler/deleate"`: Plan löschen (Typo ist absichtlich für Kompatibilität)
- **Broadcast**: Sendet `plans_updated` Event an alle WS-Clients

#### `__init__.py` - Integration-Setup
- **Setup**: `async_setup_entry()` registriert Coordinator, WS, Services
- **Unload**: `async_unload_entry()` entfernt alle Entities aus Registry
- **Registry-Cleanup**: Vor dem Unload werden alle Entities dieser Integration entfernt

---

## Services

### Plan aktiv/inaktiv über `evcc_scheduler.set_repeating_plan`

Setze das Feld `active` für bestehende Pläne (anstelle eines separaten Toggle-Services):

```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
  active: true
```
```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
  soc: 90
```

### `evcc_scheduler.del_repeating_plan`

**Beschreibung**: Lösche einen wiederkehrenden Ladeplan

**Parameter**:
```yaml
service: evcc_scheduler.del_repeating_plan
data:
  vehicle_id: "db:1"        # Fahrzeug-ID (erforderlich)
  plan_index: 1             # Plan-Index 1-basiert (erforderlich)
```

**Pflicht-/Optionale Felder**:
| Feld | Pflicht? | Hinweis |
|------|----------|---------|
| `vehicle_id` | Ja | EVCC Fahrzeug-ID (z.B. `db:1`) |
| `plan_index` | Ja | 1-basiert, muss existieren |

**Fehlerbehandlung**: Identisch mit `set_repeating_plan`

**Beispiel**:
```yaml
service: evcc_scheduler.del_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 2
```

## Datenfluss

### Startup-Prozess

```
1. async_setup_entry() aufgerufen
   ↓
2. API, Coordinator, WebSocket initialisiert
   ↓
3. coordinator.async_config_entry_first_refresh()
   ├─ _async_update_data() aufgerufen
   ├─ Liest vehicleName aus loadpoints[]
   └─ Lädt Pläne für aktives Fahrzeug
   ↓
4. switch.py setup_platform() aufgerufen
   ├─ Erstellt Entity Manager
   └─ Registriert sync() Callback
   ↓
5. entity_manager.sync() aufgerufen
   ├─ build_entity_id() für jeden Plan
   └─ async_add_entities() registriert Entities
   ↓
6. WebSocket verbunden, Services registriert
   ↓
✅ Integration ready
```

### Fahrzeugwechsel (Elroq → Eniaq)

```
1. Nutzer wählt Eniaq in EVCC UI
   ↓
2. EVCC setzt loadpoints[0].vehicleName = "db:2"
   ↓
3. WebSocket-Nachricht von EVCC empfangen
   ↓
4. websocket_client.py → coordinator.async_request_refresh()
   ↓
5. _async_update_data() lädt db:2 statt db:1
   ├─ wanted_ids = {evcc_eniaq_repeating_plan_01, evcc_eniaq_repeating_plan_02}
   └─ current_ids = {evcc_elroq_repeating_plan_01, evcc_elroq_repeating_plan_02}
   ↓
6. entity_manager.sync()
   ├─ Löscht evcc_elroq_repeating_plan_* aus entities dict
   ├─ async_remove() aus Registry
   ├─ Erstellt evcc_eniaq_repeating_plan_* neu
   └─ async_add_entities() registriert neue Entities
   ↓
✅ Eniaq-Pläne sichtbar, Elroq-Entities gelöscht
```

### Service-Aufruf (set_repeating_plan)

```
1. User-Service-Aufruf mit vehicle_id="db:1"
   ↓
2. services.py: set_repeating_plan() aufgerufen
   ├─ Holt EVCC-State
   ├─ Prüft vehicleName in loadpoints[]
   ├─ Validiert Fahrzeug-ID, Verfügbarkeit, Index
   └─ Wirft ServiceValidationError bei Fehler
   ↓
3. API: get_repeating_plans("db:1")
   ↓
4. Modifiziert plans Array lokal
   ↓
5. API: set_repeating_plans("db:1", plans)
   ↓
6. coordinator.async_request_refresh()
   ├─ Lädt aktualisierte Daten
   └─ entity_manager.sync() aktualisiert Entities
   ↓
7. WebSocket: _broadcast_plans_updated()
   ├─ Sendet Event an alle WS-Clients
   └─ Custom Card aktualisiert UI
   ↓
✅ Service erfolgreich, Daten synchronisiert
```

### Home Assistant Neustart

```
1. HA wird heruntergefahren
   ↓
2. async_unload_entry() aufgerufen
   ├─ Lädt entity_registry
   ├─ Findet alle Entities mit config_entry_id
   └─ async_remove() alle Entities
   ↓
3. HA wird hochgefahren
   ↓
4. async_setup_entry() aufgerufen (wie Startup)
   ├─ Neue Entities nur für aktuell gewähltes Fahrzeug
   └─ Registry clean, keine Zombies
   ↓
✅ Sauberer Start
```

---

## Entity-Indizes und Namenskonvention

### 1-basierte UI, 0-basierte Arrays

| Kontext | Indexierung | Beispiel |
|---------|-------------|----------|
| Home Assistant Entity-Name | 1-basiert (keine Nullen) | `evcc_elroq_repeating_plan_1_activ`, `_2_activ`, `_3_activ` |
| Entity-ID in UI/Services | 1-basiert | Plan 1, Plan 2, Plan 3 |
| EVCC JSON Array | 0-basiert | `plans[0]`, `plans[1]`, `plans[2]` |
| Interner Code | 0-basiert für Arrays | `idx = plan_index - 1` |

**Kritisch**: Service-Parameter sind 1-basiert, müssen intern zu 0-basiert konvertiert werden!

```python
# In services.py:
plan_index = call.data.get("plan_index")  # 1-basiert von Nutzer
idx = int(plan_index) - 1                 # Konvertiert zu 0-basiert
plans[idx] = {...}                        # Aktualisiert korrekten Plan
```

### Entity-ID Generation

```python
# Aus mapping.py:
def build_entity_id(vehicle_id: str, index: int, title: str = None) -> str:
    base = title if title else vehicle_id
    safe_name = base.lower().replace(":", "_").replace("-", "_").replace(" ", "_")
    return f"evcc_{safe_name}_repeating_plan_{index}_activ"  # Base-ID mit _activ

# Beispiele (Base-ID mit _activ Suffix):
build_entity_id("db:1", 1, "Elroq")    # "evcc_elroq_repeating_plan_1_activ"
build_entity_id("db:2", 2, "Eniaq")    # "evcc_eniaq_repeating_plan_2_activ"
build_entity_id("car-001", 3, "Tesla") # "evcc_tesla_repeating_plan_3_activ"

# In den Entity-Plattformen wird Suffix getauscht:
# switch.py: "...plan_1_activ" (direkt)
# time.py: base_id.replace("_activ", "_time") → "...plan_1_time"
# text.py: base_id.replace("_activ", "_weekdays") → "...plan_1_weekdays"
# number.py: base_id.replace("_activ", "_soc") → "...plan_1_soc"
```

---

## Konfiguration & Architektur-Updates

### Manifesto (manifest.json)

```json
{
  "domain": "evcc_scheduler",
  "name": "EVCC Scheduler",
   "version": "0.1.2",
  "documentation": "https://github.com/diestrohs/ha-evcc-scheduler",
  "requirements": ["aiohttp>=3.8.0"],
  "codeowners": ["@diestrohs"],
  "config_flow": true,
  "iot_class": "local_polling",
  "integration_type": "service",
  "platforms": ["switch", "time", "text", "number"],
  "homeassistant": "2025.12.0"
}
```

### Gemeinsame Basisklasse

Die Entities erben von `base_entity.py` (`BaseEvccPlanEntity`), welche gemeinsame Felder (`vehicle_id`, `plan_index`, `vehicle_title`), `update_data()` und eine Hilfsfunktion zur ID-Erzeugung (`make_unique_id`) bereitstellt.

### Const (const.py)

```python
DOMAIN = "evcc_scheduler"
DEFAULT_PORT = 7070
DEFAULT_TIMEOUT = 10
DEFAULT_WEBSOCKET = True
DEFAULT_WS_API = False
DEFAULT_POLL_INTERVAL = 30
CONF_HOST = "host"
CONF_PORT = "port"
CONF_TOKEN = "token"
CONF_SSL = "ssl"
CONF_WEBSOCKET = "websocket"
CONF_WS_API = "websocket_api"
CONF_POLL_INTERVAL = "poll_interval"
```

---

## Logging und Debugging

### Logging aktivieren

```yaml
# configuration.yaml
logger:
  logs:
    evcc_scheduler: debug
    evcc_scheduler.api: debug
    evcc_scheduler.coordinator: debug
    evcc_scheduler.websocket_client: debug
    evcc_scheduler.entity_manager: debug
```

### Wichtige Log-Messages

| Log-Level | Beispiel | Bedeutung |
|-----------|----------|-----------|
| DEBUG | `Found active vehicle in loadpoint: db:1` | Fahrzeug erkannt |
| INFO | `Loaded 3 plans for active vehicle: Elroq` | Plans geladen |
| INFO | `Created plan entity: evcc_elroq_repeating_plan_01` | Entity erstellt |
| INFO | `Removing plan entity: evcc_elroq_repeating_plan_02` | Entity gelöscht |
| WARNING | `Vehicle db:99 not found in EVCC vehicles data` | Fahrzeug nicht vorhanden |
| ERROR | `Failed to create entity xyz: ...` | Entity-Erstellung fehlgeschlagen |

### Debugging-Tipps

1. **WebSocket-Verbindung prüfen**:
   ```bash
   wscat -c ws://192.168.1.100:7070/ws
   ```

2. **API testen**:
   ```bash
   curl http://192.168.1.100:7070/api/state | jq '.loadpoints[0].vehicleName'
   curl http://192.168.1.100:7070/api/vehicles/db:1/plan/repeating
   ```

3. **Entities prüfen**:
   - Einstellungen → Geräte und Services → Entities
   - Filtern: `evcc_`

4. **Registry-Probleme**:
   ```bash
   # Manuelle Registry-Bereinigung (nur notfalls!)
   rm /config/.storage/core.entity_registry
   # HA-Neustart erforderlich
   ```

---

## Fehlerbehandlung

### Häufige Fehler

#### "Custom element doesn't exist: repeating-scheduler-card"
- **Ursache**: Custom Card nicht installiert oder falsche Imports
- **Lösung**: Card-Repository separat klonen, relative Imports auf absolute umstellen

#### "Kein Fahrzeug in EVCC gewählt"
- **Ursache**: `vehicleName` ist leer
- **Lösung**: In EVCC Fahrzeug an Ladestation anschließen oder auswählen

#### "Fahrzeug-ID stimmt nicht überein"
- **Ursache**: Service-Aufruf mit falscher Fahrzeug-ID
- **Lösung**: Korrekte ID aus Logs oder Entities verwenden

#### Entity Registry überwachsen
- **Ursache**: Nach Update alte Entities nicht gelöscht
- **Lösung**: `async_unload_entry()` testet - manuell sync() aufrufen

#### WebSocket verbindet sich nicht
- **Ursache**: EVCC offline, Port falsch, Firewall
- **Lösung**: Polling-Fallback greift nach 30s, logs prüfen

---

## Technische Spezifikationen

### EVCC API-Anforderungen

**Endpoints**:
- `GET /api/state` - Kompletter State
- `GET /api/vehicles/{id}/plan/repeating` - Pläne eines Fahrzeugs
- `POST /api/vehicles/{id}/plan/repeating` - Pläne setzen
- `ws://{host}:{port}/ws` - WebSocket

**State-Struktur**:
```json
{
  "loadpoints": [
    {
      "vehicleName": "db:1",
      "vehicleTitle": "Elroq",
      "connected": true,
      ...
    }
  ],
  "vehicles": {
    "db:1": {
      "title": "Elroq",
      "repeatingPlans": [
        {
          "time": "07:00",
          "weekdays": [1, 2, 3, 4, 5],
          "soc": 80,
          "active": true
        }
      ]
    }
  }
}
```

### Performance

| Metrik | Wert | Notiz |
|--------|------|-------|
| Polling-Intervall | 30s | Konfigurierbar, Standard 30 |
| WebSocket-Reconnect | 5s backoff | Exponentiell bis max 5 Versuche |
| HTTP Timeout | 10s | In config_flow konfigurierbar |
| Entity-Sync Zeit | <100ms | Schneller als Coordinator-Update |
| Memory pro Fahrzeug | ~5KB | Minimal (nur Pläne im RAM) |

### Kompatibilität

| Komponente | Anforderung | Getestet |
|------------|-------------|-------------|
| Home Assistant | 2025.12+ | 2025.12 ✅ |
| EVCC | 0.210.2+ | 0.210.2 ✅ |
| Python | 3.11+ | 3.12 ✅ |
| aiohttp | 3.8+ | 3.9+ ✅ |
| asyncio | Standard Library | ✅ |

---

## Beitragen und Entwicklung

### Entwicklungs-Setup

```bash
git clone https://github.com/[username]/evcc_scheduler.git
cd evcc_scheduler
pip install -e .
```

### Tests ausführen

```bash
# Derzeit keine automatisierten Tests
# Manuelles Testen erforderlich:
# 1. EVCC starten
# 2. HA starten mit custom_components/evcc_scheduler
# 3. Integration konfigurieren
# 4. Services über Developer Tools testen
```

### Code-Stil

- Python: PEP 8
- Imports: Standard → Drittparteien → Home Assistant → Lokal
- Type-Hints: Für alle Funktionen
- Logging: Verwende `_LOGGER` mit `debug`, `info`, `warning`, `error`

### Pull Request Checklist

- [ ] Funktion implementiert und getestet
- [ ] Logging hinzugefügt (debug-Level)
- [ ] Type-Hints aktualisiert
- [ ] Fehlerbehandlung berücksichtigt
- [ ] README/DOCUMENTATION aktualisiert
- [ ] Keine Breaking Changes ohne Versionsbump

---

## Lizenz

MIT License - Siehe LICENSE Datei

---

## Kontakt & Support

- **Issues**: GitHub Issues
- **Diskussionen**: GitHub Discussions
- **Lovelace Card**: Separates Repository (Link folgt)

---

**Zuletzt aktualisiert**: 24. Januar 2026  
**Version**: 0.1.2
