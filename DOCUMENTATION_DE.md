# EVCC Scheduler - Dokumentation

## Übersicht

**EVCC Scheduler** ist eine Home Assistant Custom Integration zur Verwaltung wiederkehrender EV-Ladepläne über die EVCC API. Die Integration synchronisiert die Fahrzeugauswahl mit EVCC und bietet eine zentrale Verwaltung von Ladeplänen mit automatischer Entfernung verwaister Entities.

**Lizenz:** MIT  
**Repository:** [GitHub](https://github.com/diestrohs/ha-evcc-scheduler)  
**HACS:** ✅ Kompatibel & verfügbar  
**Home Assistant:** 2025.12.0+  
**EVCC:** 0.210.2+

---

## Quick Start 🚀

### 1. Installation mit HACS (1 Minute)

```
HACS → Integrationen → ⋮ → Custom Repositories
→ https://github.com/diestrohs/ha-evcc-scheduler
→ Kategorie: Integration
→ Suche: EVCC Scheduler → Installieren
→ Home Assistant neu starten ⭐ WICHTIG
```

### 2. Konfiguration (2 Minuten)

```
Einstellungen → Geräte und Services → + Integration erstellen
→ Suche: EVCC Scheduler
→ Host: 192.168.1.100 (EVCC-IP)
→ Port: 7070 (Standard)
→ Token: (falls erforderlich)
→ SSL: (für HTTPS, optional)
→ WebSocket: Aktiviert (empfohlen, Standard)
→ Aktualisierungsintervall: 30 Sekunden (nur wenn WebSocket deaktiviert)
→ Speichern ✅
```

### 3. Fertig! 🎉

- Entities werden automatisch erstellt
- Services stehen zur Verfügung
- WebSocket läuft für Echtzeit-Updates

---

## Funktionalität

### Kerenfunktionen

- ✅ **Automatische Fahrzeugauswahl**: Erkennt das in EVCC gewählte Fahrzeug automatisch
- ✅ **Dynamische Entity-Verwaltung**: Erstellt/löscht Entities basierend auf aktuellem Fahrzeug
- ✅ **WebSocket-Integration**: Echtzeit-Updates bei Änderungen in EVCC
- ✅ **Service-Registrierung**: CRUD-Operationen für Ladepläne
- ✅ **Entity Registry Cleanup**: Automatisches Löschen verwaister Entities
- ✅ **Multi-Fahrzeug-Support**: Wechsel zwischen mehreren Fahrzeugen mit automatischer Entity-Migration
- ✅ **Fehlervalidation**: Aussagekräftige Fehlermeldungen bei Service-Aufrufen

### Unterstützte Fahrzeuge

Alle Fahrzeuge, die in EVCC konfiguriert sind:
- Tesla (Model S, 3, X, Y)
- Volkswagen (ID.4, ID.5, ID. Buzz, etc.)
- Škoda (Enyaq, Superb iV, etc.)
- Audi (e-tron, Q4 e-tron, etc.)
- Cupra
- und weitere...

---

## Installation

### Voraussetzungen

- Home Assistant 2025.12 oder neuer (getestet mit 2025.12)
- EVCC v0.210.2 oder neuer mit aktivierter REST API (getestet mit 0.210.2)
- EVCC und Home Assistant im gleichen Netzwerk (oder erreichbar)

### Installationsschritte

#### 1. Mit HACS (empfohlen) 🎉

1. Öffne HACS in Home Assistant
2. Gehe zu "Integrationen"
3. Klicke auf das Menü (oben rechts) → "Custom Repositories"
4. Füge folgende URL ein: `https://github.com/diestrohs/ha-evcc-scheduler`
5. Wähle **"Integration"** als Kategorie
6. Klicke "Erstellen"
7. Suche nach "EVCC Scheduler" und klicke "Installieren"
8. **⚠️ Wichtig**: Home Assistant neu starten erforderlich!

#### 2. Manuell (ohne HACS)

```bash
cd /config/custom_components
git clone https://github.com/diestrohs/ha-evcc-scheduler.git
# Home Assistant neu starten
```

#### 3. Integration konfigurieren

Nach der Installation und dem Neustart von Home Assistant:

1. Gehe zu **Einstellungen** → **Geräte und Services** → **Integrationen**
2. Klicke **"+ Integration erstellen"**
3. Suche nach **"EVCC Scheduler"** und wähle aus
4. Folge der Konfiguration:
   - **Host**: IP oder Hostname von EVCC (z.B. `192.168.1.100`)
   - **Port**: EVCC API Port (Default: `7070`)
   - **Token**: Optional, falls EVCC Token-Auth hat
   - **SSL**: An/Aus je nach EVCC-Setup
   - **WebSocket**: An/Aus für Echtzeit-Updates (Default: An - empfohlen)
   - **Aktualisierungsintervall**: Sekunden (Default: 30, nur wenn WebSocket AUS)

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
    └─→ switch.py (Platform-Setup)
           └─→ entity_manager.py (Entity-Lifecycle)
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
- **Aufgabe**: Zentrale Datenquelle, 30s Polling
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
- **Aufgabe**: Synchronisiert Entities mit Coordinator-Daten (optimiert für Wiederverwendung)
- **Sync-Strategie**:
  1. **Updates**: Bestehende Entities via `update_data()` aktualisieren (0 Registry-Zugriffe)
  2. **Neue**: Nur anlegen, wenn Plan-Anzahl steigt
  3. **Gelöschte**: Nur entfernen, wenn Plan-Anzahl sinkt (Registry-Cleanup nur dann)
- **Vorteile**: 
  - Fahrzeugwechsel mit gleicher Plan-Anzahl → Keine Registry-Zugriffe
  - Entity-IDs bleiben stabil
  - Automations/Scripts funktionieren ohne Neustart nach Fahrzeugwechsel

#### `switch.py` - Switch Platform
- **Entität**: `EvccPlanSwitch` für jeden Plan
- **Attribute**:
  - Plan-Details: `time`, `weekdays`, `soc`, `active`
  - Fahrzeug-Info: `vehicle_title`, `vehicle_id` (neu!)
- **Toggle**: `async_turn_on/off()` → API-Aufruf → `coordinator.async_request_refresh()`
- **Effiziente Updates**: `update_data()` Methode für Fahrzeugwechsel (keine Entity-Neuerstellung)

#### `services.py` - Service-Registrierung
- **Services**:
  - `evcc_scheduler.set_repeating_plan`
  - `evcc_scheduler.del_repeating_plan`
- **Validierung**: Prüft Fahrzeug-ID, Verfügbarkeit, Plan-Index
- **Fehlerbehandlung**: `ServiceValidationError` mit aussagekräftigen Meldungen

#### `mapping.py` - Hilfsfunktionen
- `extract_plans()`: Konvertiert EVCC-State zu vehicles-Dict
- `build_entity_id()`: Generiert eindeutige Entity-IDs (fahrzeugag-nostisch)
  - Format: `evcc_repeating_plan_{index}`
  - Beispiel: `evcc_repeating_plan_1`, `evcc_repeating_plan_2`
  - Vorteil: Entity-IDs bleiben bei Fahrzeugwechsel stabil

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

---

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
   ├─ wanted_ids = {evcc_repeating_plan_1, evcc_repeating_plan_2}
   └─ current_ids = {evcc_repeating_plan_1, evcc_repeating_plan_2}
   ↓
7. entity_manager.sync()
   ├─ Laden aktualisierte Daten mit update_data()
   ├─ Keine Registry-Zugriffe bei gleicher Plan-Anzahl
   ├─ Entity-IDs bleiben stabil!
   └─ Automations funktionieren weiter
   ↓
✅ Pläne aktualisiert, Entity-IDs bleiben gleich (fahrzeugagnostisch)
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
| Home Assistant Entity-Name | 1-basiert | `evcc_repeating_plan_1`, `evcc_repeating_plan_2`, `evcc_repeating_plan_3` |
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

**Neue Strategie (ab v0.0.4)**: Entity-IDs sind fahrzeugagnostisch und stabil über Fahrzeugwechsel:

```python
# Aus mapping.py:
def build_entity_id(vehicle_id: str, index: int) -> str:
    return f"evcc_repeating_plan_{index}"

# Beispiele:
build_entity_id("db:1", 1)  # "evcc_repeating_plan_1"
build_entity_id("db:2", 1)  # "evcc_repeating_plan_1" (gleiche ID!)
build_entity_id("car-001", 3)  # "evcc_repeating_plan_03"
```

**Vorteil**: Automations/Scripts sind fahrzeugwechsel-resistent. Die Entity-ID für "Plan 1" ist immer `switch.evcc_repeating_plan_1`, egal welches Fahrzeug aktiv ist.

---

## Konfiguration

### Manifesto (manifest.json)

```json
{
  "domain": "evcc_scheduler",
  "name": "EVCC Scheduler",
  "version": "0.0.4",
  "documentation": "https://github.com/...",
  "requirements": [],
  "codeowners": ["@username"],
  "config_flow": true,
  "iot_class": "local_polling",
  "integration_type": "service",
  "platforms": ["switch"],
  "homeassistant": "2025.12.0"
}
```

### Const (const.py)

```python
DOMAIN = "evcc_scheduler"
DEFAULT_PORT = 7070
DEFAULT_TIMEOUT = 10
CONF_TIMEOUT = "timeout"
CONF_SSL = "ssl"
CONF_MODE = "mode"
MODE_WEBSOCKET = "websocket"
MODE_POLLING = "polling"
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
| DEBUG | `Entity sync: found 1 vehicles` | Sync-Start |
| INFO | `Vehicle db:1 (Elroq) has 2 plans` | Fahrzeug + Plan-Anzahl erkannt |
| INFO | `Updated plan entity: evcc_repeating_plan_1` | Entity aktualisiert (kein Registry-Zugriff) |
| INFO | `Created plan entity: evcc_repeating_plan_03` | Entity erstellt (mehr Pläne) |
| INFO | `Removing plan entity: evcc_repeating_plan_04` | Entity gelöscht (weniger Pläne) |
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
**Version**: 0.1.0
