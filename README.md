# HA EVCC Scheduler

Home Assistant integration for managing EV charging schedules via EVCC API.

## Features

- 🚗 **Automatic Vehicle Detection**: Syncs with selected vehicle in EVCC
- ⚙️ **Dynamic Plan Management**: Create/update/delete repeating charging schedules
- 🔄 **Real-time Updates**: WebSocket support with polling fallback
- 🎛️ **Switch Entities**: Toggle plans directly from Home Assistant UI
- 🌍 **Multi-Language**: German & English support
- 📱 **Custom Card Ready**: WebSocket API for advanced UI integration
- 🧪 **Experimental Custom Card WS API**: Disabled by default, opt-in via config checkbox (untested)
- ✅ **HACS Compatible**: Install via Home Assistant Community Store

## Quick Start

### Installation (HACS)

1. Open HACS → Integrations
2. Click **⋮** → **Custom Repositories**
3. Add: `https://github.com/diestrohs/ha-evcc-scheduler`
4. Select **Integration** category
5. Search "EVCC Scheduler" → **Install**
6. **Restart Home Assistant** ⭐

### Configuration

1. Settings → Devices and Services
2. Click **+ Create Integration**
3. Search "EVCC Scheduler"
4. Enter:
   - Host: `192.168.1.100` (EVCC IP)
   - Port: `7070` (default)
   - Token: (if required)
  - Custom Card WS API (experimental): enable if you need the card API (untested)
5. Click **Submit** ✅

### Usage

- Switch entities appear as `switch.{vehicle}_plan_0{n}`
- Toggle plans directly in Home Assistant UI
- Use services to create/update/delete plans

## Documentation

- 📖 [Full Documentation (English)](./DOCUMENTATION.md)
- 📖 [Deutsche Dokumentation](./README_DE.md)
- 🚀 [HACS Installation Guide](./HACS_INSTALL.md)
- 📝 [Changelog](./CHANGELOG.md)
- 🤝 [Contributing](./CONTRIBUTING.md)

## Requirements

- Home Assistant 2025.12.0+
- EVCC 0.210.2+
- Python 3.11+
- Network access to EVCC instance

## Services

### `evcc_scheduler.set_repeating_plan`

Create or update charging plan.

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

Delete charging plan.

```yaml
service: evcc_scheduler.del_repeating_plan
data:
  vehicle_id: "vehicle:0"
  plan_index: 1
```

### `evcc_scheduler.toggle_plan_active`

Toggle plan active status.

```yaml
service: evcc_scheduler.toggle_plan_active
data:
  vehicle_id: "vehicle:0"
  plan_index: 1
  active: false
```

## Architecture

```
config_flow.py ──→ __init__.py ──→ coordinator.py ──→ api.py
    ↓                  ↓
websocket_client.py    entity_manager.py ←→ switch.py
    ↓
websocket_api.py (Custom Card API)
```

- **DataUpdateCoordinator**: 30-second polling interval
- **WebSocket**: Real-time updates with auto-reconnect
- **Entity Manager**: Automatic creation/deletion based on vehicle
- **Entity Registry**: Cleanup on restart and unload

## Troubleshooting

### Connection Issues

```bash
# Test EVCC connectivity
curl http://192.168.1.100:7070/api/state | jq '.vehicles'

# Test WebSocket
wscat -c ws://192.168.1.100:7070/ws
```

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  logs:
    evcc_scheduler: debug
    evcc_scheduler.api: debug
    evcc_scheduler.coordinator: debug
```

## Support

- 🐛 [Bug Reports](https://github.com/diestrohs/ha-evcc-scheduler/issues)
- 💬 [Discussions](https://github.com/diestrohs/ha-evcc-scheduler/discussions)
- 📚 [Full Documentation](./DOCUMENTATION.md)

## License

MIT License - See [LICENSE](./LICENSE) for details

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

---

**Version**: 0.0.4  
**Home Assistant**: 2025.12.0+  
**EVCC**: 0.210.2+  
**License**: MIT

[Deutsch / German](./README_DE.md)
cd /config/custom_components
git clone https://github.com/diestrohs/ha-evcc-scheduler.git
# Home Assistant neu starten
```

## Konfiguration

Nach der Installation:

1. Gehe zu **Einstellungen** → **Geräte und Services** → **Integrationen**
2. Klicke auf **"+ Integration erstellen"**
3. Suche nach **"EVCC Scheduler"**
4. Folge der Konfiguration:
   - **Host**: IP oder Hostname von EVCC (z.B. `192.168.1.100`)
   - **Port**: EVCC API Port (Default: `7070`)
   - **Token**: Optional (falls EVCC Token-Auth hat)
   - **SSL**: An/Aus je nach EVCC-Setup
   - **Timeout**: HTTP-Timeout in Sekunden (Default: `10`)

## Verwendung

### Services

Die Integration stellt folgende Services zur Verfügung:

#### `evcc_scheduler.set_repeating_plan`
Erstelle oder aktualisiere einen Ladeplan

```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1              # Optional: null = neuer Plan
  time: "07:00"
  weekdays: [1, 2, 3, 4, 5]  # 1=Mo, 7=So
  soc: 80
  active: true
```

#### `evcc_scheduler.del_repeating_plan`
Lösche einen Ladeplan

```yaml
service: evcc_scheduler.del_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
```

#### `evcc_scheduler.toggle_plan_active`
Schalte einen Plan aktiv/inaktiv

```yaml
service: evcc_scheduler.toggle_plan_active
data:
  vehicle_id: "db:1"
  plan_index: 1
  active: true  # Optional: null = toggle
```

### Entities

Pro Ladeplan wird eine Switch-Entity erstellt:
- `switch.evcc_[fahrzeug]_repeating_plan_[nr]`

Die Entity zeigt den Status des Plans und weitere Attribute:
- `time`: Startzeit des Plans
- `weekdays`: Wochentage
- `soc`: Ladeziel in %
- `active`: Status

## Dokumentation

Detaillierte Dokumentation:
- [DOCUMENTATION.md](DOCUMENTATION.md) - Vollständige Technische Dokumentation
- [CARD_README.md](CARD_README.md) - Custom Lovelace Card Installation

## Voraussetzungen

- Home Assistant 2025.12 oder neuer
- EVCC v0.210.2 oder neuer mit aktivierter REST API
- EVCC und Home Assistant im gleichen Netzwerk (oder erreichbar)
- Python 3.11+

## Unterstützte Fahrzeuge

Alle Fahrzeuge, die in EVCC konfiguriert sind:
- Tesla (Model S, 3, X, Y)
- Volkswagen (ID.4, ID.5, ID. Buzz, ID.3, etc.)
- Škoda (Enyaq, Superb iV, Citigo iV, etc.)
- Audi (e-tron, Q4 e-tron, e-tron GT, etc.)
- Cupra (Born, Leon, etc.)
- BMW (i3, i4, iX, etc.)
- Mercedes (EQA, EQC, EQE, EQS, etc.)
- Hyundai (Ioniq, Kona, Tucson, etc.)
- Kia (e-Niro, EV9, EV6, etc.)
- Nissan (Leaf, Ariya, etc.)
- Polestar (1, 2, 3, etc.)
- Porsche (Taycan, etc.)
- Und weitere...

## Fehlerbehandlung

Wenn die Integration nicht funktioniert:

1. **Logs prüfen**: 
   ```yaml
   logger:
     logs:
       evcc_scheduler: debug
   ```

2. **EVCC-Verbindung testen**:
   ```bash
   curl http://192.168.1.100:7070/api/state | jq '.vehicles'
   ```

3. **WebSocket testen**:
   ```bash
   wscat -c ws://192.168.1.100:7070/ws
   ```

## Support

- 🐛 [Bug Reports](https://github.com/diestrohs/ha-evcc-scheduler/issues)
- 💬 [Diskussionen](https://github.com/diestrohs/ha-evcc-scheduler/discussions)
- 📚 [Dokumentation](https://github.com/diestrohs/ha-evcc-scheduler/wiki)

## Lizenz

MIT License - Siehe [LICENSE](LICENSE) Datei

## Beitragen

Beiträge sind willkommen! Bitte lese [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

---

**Getestet mit:**
- Home Assistant 2025.12 ✅
- EVCC 0.210.2 ✅
- Python 3.12 ✅
