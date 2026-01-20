# HA EVCC Scheduler

Home Assistant integration for managing EV charging schedules via EVCC API.

## Features

- 🚗 **Automatic Vehicle Detection**: Syncs with selected vehicle in EVCC
- ⚙️ **Dynamic Plan Management**: Create/update/delete repeating charging schedules
- 🔄 **Real-time Updates**: WebSocket support with polling fallback
- 🎛️ **Switch Entities**: Toggle plans directly from Home Assistant UI
- 🌍 **Multi-Language**: German & English support
- 📱 **Custom Card Ready**: WebSocket API for advanced UI integration
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
5. Click **Submit** ✅

### Usage

- Switch entities appear as `switch.{vehicle}_plan_0{n}`
- Toggle plans directly in Home Assistant UI
- Use services to create/update/delete plans

## Documentation

- 📖 [Full Documentation (German)](./DOCUMENTATION.md)
- 📖 [Full Documentation (English)](./DOCUMENTATION_EN.md)
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
- 📚 [Full Documentation](./DOCUMENTATION_EN.md)

## License

MIT License - See [LICENSE](./LICENSE) for details

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

---

**Version**: 0.0.4  
**Home Assistant**: 2025.12.0+  
**EVCC**: 0.210.2+  
**License**: MIT
