# EVCC Scheduler Integration für Home Assistant

Eine Home Assistant Custom Integration zur Verwaltung wiederkehrender EV-Ladepläne über die EVCC API.

## Features

- ✅ Automatische Fahrzeugauswahl aus EVCC
- ✅ Dynamische Entity-Verwaltung (Erstellen/Löschen basierend auf Fahrzeugwechsel)
- ✅ WebSocket-Integration für Echtzeit-Updates
- ✅ Service-Registrierung für CRUD-Operationen
- ✅ Entity Registry Cleanup bei Neustart
- ✅ Multi-Fahrzeug-Support mit automatischer Entity-Migration
- ✅ Aussagekräftige Fehlerbehandlung und Validierung

## Installation

### Mit HACS (empfohlen)

1. Öffne HACS in Home Assistant
2. Gehe zu "Integrationen"
3. Klicke auf das Menü (oben rechts) → "Custom Repositories"
4. Füge folgende URL ein: `https://github.com/diestrohs/ha-evcc-scheduler`
5. Wähle "Integration" als Kategorie
6. Klicke "Erstellen"
7. Suche nach "EVCC Scheduler" und klicke "Installieren"
8. **Wichtig**: Starte Home Assistant neu

### Manuell

```bash
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
