# EVCC Scheduler Integration für Home Assistant

Eine Home Assistant Custom Integration zur Verwaltung wiederkehrender EV-Ladepläne über die EVCC API.

## Features

- 🚗 **Automatische Fahrzeugauswahl**: Erkennt das in EVCC gewählte Fahrzeug automatisch
- ⚙️ **Dynamische Plan-Verwaltung**: Erstelle/aktualisiere/lösche wiederkehrende Ladepläne
- 🔄 **Echtzeit-Updates**: WebSocket-Support mit Polling-Fallback
- 🎛️ **Switch-Entities**: Schalte Pläne direkt aus der Home Assistant UI
- 🌍 **Mehrsprachig**: Deutsch & Englisch Support
- 📱 **Custom Card Ready**: WebSocket API für erweiterte UI-Integration
- 🧪 **Experimentelle Custom Card WS-API**: Standardmäßig aus, optional per Checkbox aktivierbar (nicht getestet)
- ✅ **HACS-kompatibel**: Installation über Home Assistant Community Store

## Quick Start

### Installation (HACS)

1. Öffne HACS in Home Assistant
2. Gehe zu "Integrationen"
3. Klicke **⋮** → **Custom Repositories**
4. Füge ein: `https://github.com/diestrohs/ha-evcc-scheduler`
5. Wähle **Integration** als Kategorie
6. Suche "EVCC Scheduler" → **Installieren**
7. **Starte Home Assistant neu** ⭐

### Konfiguration

1. Einstellungen → Geräte und Services
2. Klicke **+ Integration erstellen**
3. Suche "EVCC Scheduler"
4. Gib ein:
   - **Name** (optional): Benutzerdefinierter Name für diese Integration
   - **Host**: EVCC IP-Adresse (z.B. `192.168.1.100`)
   - **Port**: EVCC-Port (Standard: `7070`)
   - **Token**: Authentifizierungstoken (optional)
   - **SSL**: Für HTTPS-Verbindungen aktivieren (optional)
   - **WebSocket**: Für Echtzeit-Updates aktivieren (empfohlen, Standard: aktiviert)
   - **Aktualisierungsintervall**: Sekunden (Standard: `30`, nur wenn WebSocket deaktiviert)
   - **WebSocket API**: Für Custom Lovelace Card Integration (experimentell, optional)
5. Klicke **Speichern** ✅
5. Klicke **Absenden** ✅

### Verwendung

Pro Ladeplan werden vier Entities erstellt:

- **Switch**: `switch.evcc_{fahrzeug}_repeating_plan_{index}_activ` – Plan aktiv/inaktiv
  - Beispiel: `switch.evcc_elroq_repeating_plan_1_activ`
- **Time**: `time.evcc_{fahrzeug}_repeating_plan_{index}_time` – Startzeit `HH:MM`
  - Icon: `mdi:clock-digital`
- **Text**: `text.evcc_{fahrzeug}_repeating_plan_{index}_weekdays` – Wochentage (Komma-separiert: `1,2,3,4,5`)
- **Number**: `number.evcc_{fahrzeug}_repeating_plan_{index}_soc` – Zielladung in % (0–100)
  - Icon: `mdi:battery-charging` (UI-Slider Schrittweite 10; Services akzeptieren jeden Integer 0–100)

Attribute:
- Alle Entities: `vehicle_id`, `vehicle_title`, `plan_index`
- Switch zusätzlich: `time`, `weekdays`, `soc`, `active`
- Text zusätzlich: `weekdays_list`

Hinweise:
- Entity-IDs enthalten das Fahrzeug (z. B. `elroq`) und sind 1-basiert ohne führende Nullen
- Umschalten des Status erfolgt über den Switch oder per Service (`active`-Feld)

### Architektur-Hinweise

- Gemeinsame Basisklasse: `base_entity.py` (`BaseEvccPlanEntity`)
  - Stellt gemeinsame Felder bereit (`vehicle_id`, `vehicle_title`, `plan_index`), `update_data()` und ID-Helfer
- Vereinheitlichtes Plattform-Setup via `setup_platform()` (weniger Boilerplate, identisches Verhalten)

## Dokumentation

- 📖 [Vollständige Dokumentation](./DOCUMENTATION_DE.md)
- 📖 [Full Documentation (English)](./README.md)
- 🚀 [HACS Installationsanleitung](./HACS_INSTALL.md)
- 📝 [Changelog](./CHANGELOG.md)
- 🤝 [Beitragen](./CONTRIBUTING.md)

## Anforderungen

- Home Assistant 2025.12.0+
- EVCC 0.210.2+
- Python 3.11+
- Netzwerkzugriff auf EVCC-Instanz

## Services

### `evcc_scheduler.set_repeating_plan`

Erstelle oder aktualisiere einen wiederkehrenden Ladeplan.

**Parameter:**
- `vehicle_id` (erforderlich): Fahrzeug-ID von EVCC (z.B. `db:1`)
- `plan_index` (optional): Plan-Nummer (1-basiert). Weglassen = neuer Plan
- `time` (optional): Startzeit im Format HH:MM (24h)
- `weekdays` (optional): Wochentage [1=Mo, 2=Di, 3=Mi, 4=Do, 5=Fr, 6=Sa, 7=So]
- `soc` (optional): Ladeziel (1-100%)
- `active` (optional): Plan ist aktiv (true/false, Standard: true)
 - `tz` (optional): IANA-Zeitzone (Standard ist Home Assistant-Zeitzone)
 - `precondition` (optional): Enum — 0=keine Vorbedingung, 1=nur PV-Überschuss, 2=nur günstige Preise (Standard 0)

**Neuen Plan erstellen:**
```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  time: "07:00"
  tz: "Europe/Berlin"
  weekdays: [1, 2, 3, 4, 5]
  soc: 80
  precondition: 1
  active: true
```

**Existierenden Plan aktualisieren:**
```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
  soc: 90
```

**Plan-Status umschalten:**
```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
  active: false
```

### `evcc_scheduler.del_repeating_plan`

Lösche einen wiederkehrenden Ladeplan.

**Parameter:**
- `vehicle_id` (erforderlich): Fahrzeug-ID von EVCC (z.B. `db:1`)
- `plan_index` (erforderlich): Plan-Nummer zum Löschen (1-basiert)

```yaml
service: evcc_scheduler.del_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
```

#### Eingabevalidierung

- `time` muss `HH:MM` sein (00:00–23:59)
- `weekdays` muss eine nicht-leere Liste aus Ganzzahlen 1–7 sein
- `soc` muss eine Ganzzahl im Bereich 0–100 sein
- `active` muss ein boolescher Wert sein
- `precondition` muss 0, 1 oder 2 sein (Enum)

## Architektur

```
config_flow.py ──→ __init__.py ──→ coordinator.py ──→ api.py
    ↓                  ↓
websocket_client.py    entity_manager.py ←→ switch.py
    ↓
websocket_api.py (Custom Card API)
```

- **DataUpdateCoordinator**: 30-Sekunden-Polling-Intervall
- **WebSocket**: Echtzeit-Updates mit automatischer Wiederverbindung
- **Entity Manager**: Automatisches Erstellen/Löschen basierend auf Fahrzeug
- **Entity Registry**: Cleanup beim Neustart und Entladen

## Fehlerbehebung

### Verbindungsprobleme

```bash
# Teste EVCC-Konnektivität
curl http://192.168.1.100:7070/api/state | jq '.vehicles'

# Teste WebSocket
wscat -c ws://192.168.1.100:7070/ws
```

### Debug-Protokollierung aktivieren

Füge zu `configuration.yaml` hinzu:

```yaml
logger:
  logs:
    evcc_scheduler: debug
    evcc_scheduler.api: debug
    evcc_scheduler.coordinator: debug
```

## Support

- 🐛 [Bug-Berichte](https://github.com/diestrohs/ha-evcc-scheduler/issues)
- 💬 [Diskussionen](https://github.com/diestrohs/ha-evcc-scheduler/discussions)
- 📚 [Vollständige Dokumentation](./DOCUMENTATION_DE.md)

## Lizenz

MIT Lizenz - Siehe [LICENSE](./LICENSE) für Details

## Changelog

Siehe [CHANGELOG.md](./CHANGELOG.md) für Versionsverlauf.

---

**Version**: 0.1.4  
**Home Assistant**: 2025.12.0+  
**EVCC**: 0.210.2+  
**Lizenz**: MIT

**Zuletzt aktualisiert**: 24. Januar 2026

[English](./README.md)
