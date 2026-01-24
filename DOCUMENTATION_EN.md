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
- ✅ **Plan Management**: 3 services for creating, updating, deleting plans
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
                  ↓
                 base_entity.py (shared)
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

1. Go to: **Settings → Devices and Services**
2. Click **+ Create Integration**
3. Search for **"EVCC Scheduler"**
4. Select it and enter:
   - **Name** (optional): Custom name for this integration
   - **Host**: EVCC IP address (e.g., `192.168.1.100`)
   - **Port**: EVCC port (default: `7070`)
   - **Token**: If EVCC requires authentication (optional)
   - **SSL**: Enable for HTTPS connections (optional)
   - **WebSocket**: Enable for real-time updates (recommended, default: enabled)
   - **Polling Interval**: Seconds (default: `30`, only when WebSocket disabled)
   - **WebSocket API**: For custom Lovelace Card integration (experimental, optional)

5. Click **Submit** ✅

---

## Configuration

### Configuration Flow Options

| Option | Default | Description |
|--------|---------|-------------|
| **Name** | (auto: host:port) | Custom integration name |
| **Host** | Required | EVCC hostname or IP address |
| **Port** | 7070 | EVCC API port |
| **SSL** | Disabled | SSL-secured connection (https://) |
| **Token** | (empty) | Authentication token if required |
| **WebSocket** | Enabled | Use WebSocket for real-time updates |
| **Polling Interval** | 30s | Polling interval (only when WebSocket disabled) |
| **WebSocket API** | Disabled | Enable for custom Lovelace Card integration |

### WebSocket vs. Polling

- **WebSocket (Recommended)**: Real-time updates, lower latency
  - Requires EVCC 0.210.2+
  - Automatic reconnection with exponential backoff
  - Fallback to polling if connection lost

- **Polling**: Updates every 30 seconds (configurable)
  - Works with all EVCC versions
  - Higher latency, slightly higher CPU usage
  - Only used if WebSocket is disabled

---

## Entities

The integration creates four entity types per repeating plan to edit all properties individually.

### Entity Platforms

#### 1) Switch — Plan Active/Inactive
- **Entity ID**: `switch.evcc_{vehicle}_repeating_plan_{index}_activ`
- **Example**: `switch.evcc_elroq_repeating_plan_1_activ`
- **Icon**: default (system switch)
- **Attributes (full plan)**: `time`, `weekdays`, `soc`, `active` + `vehicle_id`, `vehicle_title`, `plan_index`
- **Behavior**: Loads all plans, modifies only `active`, pushes full array back, then refreshes coordinator

#### 2) Time — Plan Start Time
- **Entity ID**: `time.evcc_{vehicle}_repeating_plan_{index}_time`
- **Example**: `time.evcc_elroq_repeating_plan_1_time`
- **Icon**: `mdi:clock-digital`
- **Format**: `HH:MM` (24-hour)
- **Attributes (minimal)**: `vehicle_id`, `vehicle_title`, `plan_index`

#### 3) Text — Plan Weekdays
- **Entity ID**: `text.evcc_{vehicle}_repeating_plan_{index}_weekdays`
- **Example**: `text.evcc_elroq_repeating_plan_1_weekdays`
- **Format**: comma-separated string, e.g. `"1,2,3,4,5"` (1=Mon ... 7=Sun)
- **Attributes (minimal + list)**: `vehicle_id`, `vehicle_title`, `plan_index`, `weekdays_list`

#### 4) Number — Plan Target SOC
- **Entity ID**: `number.evcc_{vehicle}_repeating_plan_{index}_soc`
- **Example**: `number.evcc_elroq_repeating_plan_1_soc`
- **Icon**: `mdi:battery-charging`
- **Range**: 0–100 (%). UI slider uses step `10`; services can set any integer 0–100.
- **Attributes (minimal)**: `vehicle_id`, `vehicle_title`, `plan_index`

### Entity ID Generation
- Base ID: `evcc_{vehicle}_repeating_plan_{index}_activ`
- Suffix per platform: `_activ` → `_time` / `_weekdays` / `_soc`
- Vehicle ID sanitization: `lower()` and replace `:`, `-`, spaces with `_`

### Indexing: 1-based UI, 0-based arrays
- UI entities use 1-based indexing: plan 1, 2, 3
- EVCC plan arrays are 0-based: `plans[index - 1]`
- No leading zeros: `..._1_activ`, not `..._01_activ`

### Available Services

#### `evcc_scheduler.set_repeating_plan`

Create or update a repeating charging plan.

**Service Call Example:**

```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
  time: "07:00"
  weekdays: [1, 2, 3, 4, 5]
  soc: 80
  active: true
```

**Parameters (Required):**

| Parameter | Type | Description |
|-----------|------|-------------|
| `vehicle_id` | string | Vehicle ID from EVCC (e.g., `db:1`) |

**Parameters (Optional):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `plan_index` | integer | - | Plan number to create/update (1-based). Omit to create new plan |
| `time` | string | - | Time in HH:MM format (24h) |
| `weekdays` | array | - | Days: [1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat, 7=Sun] |
| `soc` | integer | - | Target SOC: 1-100 (%) |
| `active` | boolean | `true` | Plan is active |

Note: The UI number slider uses step `10`, but services can set any integer between 0 and 100.

**Toggle Plan Active:**

To activate/deactivate an existing plan without modifying other fields:

```yaml
service: evcc_scheduler.set_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
  active: false
```

---

#### `evcc_scheduler.del_repeating_plan`

Delete a specific repeating plan.

**Service Call Example:**

```yaml
service: evcc_scheduler.del_repeating_plan
data:
  vehicle_id: "db:1"
  plan_index: 1
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `vehicle_id` | string | Yes | Vehicle ID from EVCC (e.g., `db:1`) |
| `plan_index` | integer | Yes | Plan number to delete (1-based) |

---
## Debugging & Troubleshooting

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  logs:
    evcc_scheduler: debug
    evcc_scheduler.api: debug
    evcc_scheduler.coordinator: debug
    evcc_scheduler.websocket: debug
```

Restart Home Assistant and check logs in **Settings → System → Logs**.

### Common Issues

#### 1. "Integration Not Found"

**Symptom**: Integration doesn't appear in list
**Solution**:
- Ensure HACS custom repository is added correctly
- Clear browser cache (Ctrl+Shift+Delete)
- Home Assistant restart required

#### 2. "Connection Refused"

**Symptom**: `[Errno 111] Connection refused`
**Solution**:
- Verify EVCC host and port (default: 7070)
- Check firewall/network connectivity
- Test: `curl http://192.168.1.100:7070/api/state`

#### 3. "No Entities Appear"

**Symptom**: Integration installed but no switch entities
**Solution**:
- Check EVCC has at least one repeating plan
- Enable debug logging and check logs
- Verify vehicle_id format (e.g., `vehicle:0`)

#### 4. "WebSocket Connection Failed"

**Symptom**: WebSocket errors in logs
**Solution**:
- Switch to Polling mode temporarily
- Update EVCC to 0.210.2+
- Check WebSocket endpoint: `ws://host:7070/ws`

#### 5. "Entity Not Updating"

**Symptom**: Switch doesn't reflect plan changes
**Solution**:
- Force coordinator refresh via UI (reload integration)
- Check WebSocket connection status
- Verify EVCC API responds correctly: `curl http://host:7070/api/state`

### Testing EVCC Connectivity

```bash
# Test REST API
curl http://192.168.1.100:7070/api/state | jq '.vehicles'

# Test WebSocket endpoint
wscat -c ws://192.168.1.100:7070/ws

# View repeating plans
curl http://192.168.1.100:7070/api/vehicles/vehicle:0/plan/repeating
```

---

## Development

### Repository Structure

```
custom_components/evcc_scheduler/
├── __init__.py                 # Integration setup
├── api.py                      # REST/WebSocket API client
├── config_flow.py              # Configuration UI
├── const.py                    # Constants (domain, ports, etc.)
├── coordinator.py              # DataUpdateCoordinator
├── entity_manager.py           # Dynamic entity lifecycle
├── base_entity.py              # Shared base entity for plan entities
├── mapping.py                  # Data extraction & mapping
├── services.py                 # Service registration
├── services.yaml               # Service definitions
├── switch.py                   # Switch platform
├── time.py                     # Time platform
├── text.py                     # Text platform
├── number.py                   # Number platform
├── websocket_api.py            # Custom Card API
├── websocket_client.py         # WebSocket connection
├── manifest.json               # Integration manifest
├── hacs.json                   # HACS configuration
├── translations/               # i18n files
│   ├── de.json                 # German
│   └── en.json                 # English
└── www/                        # Custom card assets (optional)
```

### Key Data Structures

**Coordinator Data:**

```python
{
    "vehicles": {
        "vehicle:123": {
            "title": "Tesla Model 3",
            "repeatingPlans": [
                {
                    "time": "07:00",
                    "weekdays": [1, 2, 3, 4, 5],
                    "soc": 80,
                    "active": True
                }
            ]
        }
    }
}
```

**Plan Indexing:**
- EVCC: 0-based array (`plans[0]`, `plans[1]`)
- Home Assistant UI: 1-based entity names (`plan_01`, `plan_02`)
- Services: 1-based parameters (user-friendly)

### Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Testing

No automated test suite yet. Manual testing:

1. Use Home Assistant UI → Developer Tools → Services
2. Call services with test data
3. Check entity updates
4. Verify logs (DEBUG mode)

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history and release notes.

---

## Support

- 🐛 [Report Bugs](https://github.com/diestrohs/ha-evcc-scheduler/issues)
- 💬 [Discussions](https://github.com/diestrohs/ha-evcc-scheduler/discussions)
- 📚 [Documentation](https://github.com/diestrohs/ha-evcc-scheduler)

---

## License

MIT License - See [LICENSE](./LICENSE) for details.

---

**Last Updated**: January 24, 2026  
**Version**: 0.1.2  
**Maintainer**: [@diestrohs](https://github.com/diestrohs)
