# HA EVCC Scheduler

Home Assistant integration for managing EV charging schedules via EVCC API.

**Repository Topics**: `homeassistant`, `integration`, `evcc`, `ev-charging`, `hacs`  
**Description**: Home Assistant integration for managing EV charging schedules via EVCC API

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
   - **Host**: EVCC IP address (e.g., `192.168.1.100`)
   - **Port**: EVCC port (default: `7070`)
   - **Token**: If EVCC requires authentication (optional)
   - **SSL**: Enable for HTTPS connections (optional)
   - **WebSocket**: Enable for real-time updates (recommended, default: enabled)
   - **Polling Interval**: Seconds (default: `30`, only used if WebSocket disabled)
   - **WebSocket API**: For custom Lovelace Card integration (experimental, optional)
5. Click **Submit** ✅

**Note**: Entity IDs remain stable across vehicle changes - automations don't break!

## HACS Status ✅

This integration is **fully HACS compatible**:

- ✅ Custom Repository ready (install via HACS with custom repo URL)
- ✅ manifest.json with all required fields
- ✅ hacs.json configured correctly
- 📋 GitHub Releases (optional, not required for HACS custom repo)
- ℹ️ Home Assistant Brands (optional, only for HACS default store)

**Installation via HACS Custom Repository:**
```
HACS → Integraciones → ⋮ Menú → Custom Repositories
→ https://github.com/diestrohs/ha-evcc-scheduler
→ Categoría: Integration
→ EVCC Scheduler → Instalar
```

See [HACS Integration Guide](./HACS_INTEGRATION.md) for details.

## Documentation

- 📖 [Full Documentation (English)](./DOCUMENTATION.md)
- 📖 [Deutsche Dokumentation](./README_DE.md)
- 📋 [HACS Integration Guide](./HACS_INTEGRATION.md)
- 🏷️ [GitHub Releases & Versioning](./GITHUB_RELEASES.md)
- ✅ [HACS Compatibility Checklist](./HACS_CHECKLIST.md)
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

Create or update a repeating charging plan.

**Parameters:**
- `vehicle_id` (required): Vehicle ID from EVCC (e.g., `db:1`)
- `plan_index` (optional): Plan number (1-based). Omit to create new plan
- `time` (optional): Start time in HH:MM format (24h)
- `weekdays` (optional): Weekdays [1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat, 7=Sun]
- `soc` (optional): Target state of charge (1-100%)
- `active` (optional): Plan is active (true/false, default: true)
 - `tz` (optional): IANA timezone (defaults to Home Assistant timezone)
 - `precondition` (optional): boolean or 0/1 (defaults to 0)

**Create new plan:**
```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  time: "07:00"
  tz: "Europe/Berlin"
  weekdays: [1, 2, 3, 4, 5]
  soc: 80
  active: true
```

**Update existing plan:**
```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
  soc: 90
```

**Toggle plan active status:**
```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
  active: false
```

### `evcc_scheduler.del_repeating_plan`

Delete a repeating charging plan.

**Parameters:**
- `vehicle_id` (required): Vehicle ID from EVCC (e.g., `db:1`)
- `plan_index` (required): Plan number to delete (1-based)

```yaml
service: evcc_scheduler.del_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
```

#### Input Validation

- Time must be `HH:MM` (00:00–23:59)
- Weekdays must be a non-empty list of integers 1–7
- SOC must be an integer in range 0–100
- Active must be boolean
- Precondition must be boolean or 0/1 (normalized)

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

**Version**: 0.1.3  
**Home Assistant**: 2025.12.0+  
**EVCC**: 0.210.2+  
**License**: MIT

**Last Updated**: January 24, 2026

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

#### Plan aktiv/inaktiv setzen
Nutze `evcc_scheduler.set_repeating_plan` mit dem Feld `active`:

```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
  active: true
```

### Entities

Pro Ladeplan werden 4 Entities erstellt:

- **Switch**: `switch.evcc_elroq_repeating_plan_1_activ` - Plan aktivieren/deaktivieren
- **Time**: `time.evcc_elroq_repeating_plan_1_time` - Startzeit des Plans
- **Text**: `text.evcc_elroq_repeating_plan_1_weekdays` - Wochentage (kommagetrennt: 1,2,3,4,5)
- **Number**: `number.evcc_elroq_repeating_plan_1_soc` - Ladeziel in % (0-100)

**Entity-Attribute** (in allen Entities verfügbar):
- `vehicle_id`: Fahrzeug-ID (z.B. `db:1`)
- `vehicle_title`: Fahrzeugname (z.B. `Elroq`)
- `plan_index`: Plan-Nummer (1-basiert)
- `time`, `weekdays`, `soc`, `active`: Plan-Details (nur in Switch-Entity)
- `weekdays_list`: Wochentage als Liste (nur in Text-Entity)

**Hinweis**: Entity-IDs bleiben stabil bei Fahrzeugwechsel - Automationen funktionieren weiter!

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
