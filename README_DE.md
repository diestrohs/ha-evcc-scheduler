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
   - Host: `192.168.1.100` (EVCC IP)
   - Port: `7070` (Standard)
   - Token: (falls erforderlich)
  - Custom Card WS API (experimentell): aktivieren, wenn die Card-API benötigt wird (noch ungetestet)
5. Klicke **Absenden** ✅

### Verwendung

- Switch-Entities erscheinen als `switch.evcc_{fahrzeug}_repeating_plan_0{n}`
- Schalte Pläne direkt in der Home Assistant UI
- Nutze Services zum Erstellen/Aktualisieren/Löschen von Plänen

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

Erstelle oder aktualisiere einen Ladeplan.

```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "vehicle:0"
  plan_index: 1
  time: "07:00"
  weekdays: [1, 2, 3, 4, 5]
  soc: 80
  active: true
```

### `evcc_scheduler.del_repeating_plan`

Lösche einen Ladeplan.

```yaml
service: evcc_scheduler.del_repeating_plan
data:
  vehicle_id: "vehicle:0"
  plan_index: 1
```

### `evcc_scheduler.toggle_plan_active`

Schalte den aktiven Status eines Plans um.

```yaml
service: evcc_scheduler.toggle_plan_active
data:
  vehicle_id: "vehicle:0"
  plan_index: 1
  active: false
```

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

**Version**: 0.0.4  
**Home Assistant**: 2025.12.0+  
**EVCC**: 0.210.2+  
**Lizenz**: MIT

[English](./README.md)
