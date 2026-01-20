# EVCC Scheduler - Lovelace Card

Eine Home Assistant Custom Card für die Verwaltung wiederholender EVCC-Ladepläne.

## Installation

1. Die Card ist automatisch in der Integration enthalten
2. In deiner `configuration.yaml` oder Lovelace UI hinzufügen:

```yaml
# Über UI: Dashboard → Bearbeiten → Karte hinzufügen → Benutzerdefiniert
```

## Verwendung in Lovelace

### YAML-Konfiguration

```yaml
views:
  - title: EVCC
    cards:
      - type: custom:repeating-scheduler-card
        vehicle_id: "vehicle:123"
```

### UI-Editor

1. Dashboard öffnen
2. "Karte hinzufügen" → "Benutzerdefiniert"
3. Typ: `repeating-scheduler-card`
4. `vehicle_id` eingeben (z.B. `vehicle:123`)

## Konfiguration

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|-----|--------|-------------|
| `vehicle_id` | String | Ja | Die EVCC Fahrzeug-ID |
| `title` | String | Nein | Benutzerdef. Titel (sonst EVCC-Titel) |

## Features

✅ Liste aller wiederholenden Pläne
✅ Wochentage anzeigen (formatiert)
✅ Uhrzeit und Ladeziel anzeigen
✅ Plan aktivieren/deaktivieren (Toggle)
✅ Plan löschen
✅ Plan hinzufügen (in Planung)

## Wochentag-Formatierung

- `[1]` → `Mo`
- `[1,2,3,4,5]` → `Mo – Fr`
- `[6,7]` → `Sa – So`
- `[1,2,3,4,5,6,7]` → `Täglich`
- Sonstige → Individuelle Tage aufgelistet

## WebSocket-Kommunikation

Die Card verwendet WebSocket-Commands zur Kommunikation mit der Backend-Integration:

### Pläne abrufen
```javascript
const result = await hass.callWS({
  type: "scheduler/get",
  vehicle_id: "vehicle:123"
});
```

### Plan bearbeiten
```javascript
await hass.callWS({
  type: "scheduler/edit",
  vehicle_id: "vehicle:123",
  plan_index: 1,  // 1-basiert
  active: true,
  time: "07:00",
  soc: 80,
  weekdays: [1, 2, 3, 4, 5]
});
```

### Plan hinzufügen
```javascript
await hass.callWS({
  type: "scheduler/add",
  vehicle_id: "vehicle:123",
  time: "07:00",
  soc: 80,
  weekdays: [1, 2, 3, 4, 5],
  active: true
});
```

### Plan löschen
```javascript
await hass.callWS({
  type: "scheduler/deleate",
  vehicle_id: "vehicle:123",
  plan_index: 1  // 1-basiert
});
```

## Wochentag-Format

Für WebSocket-Commands verwende 1-basierte Indexierung:
- `1` = Montag
- `2` = Dienstag
- `3` = Mittwoch
- `4` = Donnerstag
- `5` = Freitag
- `6` = Samstag
- `7` = Sonntag

## Styling

Die Card verwendet CSS-Variablen für das Theming:

```css
--primary-color: #2196f3
--danger-color: #f44336
--success-color: #4caf50
--warning-color: #ff9800
--text-primary: #ffffff
--text-secondary: #b0bec5
--bg-primary: #263238
--bg-secondary: #37474f
```

## Fehlerbehebung

### Card wird nicht angezeigt
1. Home Assistant neu starten
2. Browser-Cache leeren
3. Lovelace Dashboard neuladen (F5)
4. In der Browser-Konsole auf Fehler prüfen (F12)

### WebSocket-Fehler
1. Integration ist korrekt konfiguriert?
2. `vehicle_id` ist korrekt?
3. EVCC läuft?
4. Netzwerkverbindung OK?

## Entwicklung

### Lokale Änderungen testen
1. Card-Dateien in `custom_components/evcc_scheduler/www/` ändern
2. Home Assistant Dashboard neuladen (Ctrl+F5)
3. Browser-Konsole auf Fehler prüfen
