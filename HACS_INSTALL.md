# HACS Installation Guide

Diese Dokumentation erklärt, wie man EVCC Scheduler über HACS installiert.

## Was ist HACS?

[HACS](https://hacs.xyz/) (Home Assistant Community Store) ist ein Manager für benutzerdefinierte Integrationen und Automatisierungen in Home Assistant. Mit HACS kannst du Integrationen viel einfacher installieren und updaten.

## Voraussetzungen

- Home Assistant 2025.12 oder neuer
- HACS installiert (Siehe [hacs.xyz Installation](https://hacs.xyz/docs/setup/prerequisites))
- Admin-Zugriff auf Home Assistant

## Installation mit HACS

### Schritt 1: Custom Repository hinzufügen

1. Öffne Home Assistant
2. Gehe zu **HACS** (sollte im Menü sein, wenn installiert)
3. Klicke oben rechts auf das **⋮ (Menü)-Symbol**
4. Wähle **"Custom Repositories"**

### Schritt 2: Repository URL eingeben

1. Gib folgende URL ein:
   ```
   https://github.com/diestrohs/ha-evcc-scheduler
   ```
2. Wähle als **Kategorie**: `Integration`
3. Klicke **"Erstellen"**

### Schritt 3: Installation durchführen

1. Nach dem Hinzufügen erscheint die Integration in HACS
2. Suche nach **"EVCC Scheduler"**
3. Klicke auf die Integration
4. Klicke den **"Installieren"-Button** (unten rechts)
5. Warte auf den Abschluss der Installation

### Schritt 4: Home Assistant neu starten 🔄

**⚠️ Dieser Schritt ist sehr wichtig!**

```
Einstellungen → System → Neustart
(oder)
Entwickler-Tools → YAML → Neustart
(oder)
Systembefehl: homeassistant-cli service home_assistant.restart
```

## Konfiguration nach Installation

Nach dem Neustart erscheint die Integration automatisch im Config Flow:

1. Gehe zu **Einstellungen** → **Geräte und Services** → **Integrationen**
2. Suche nach **"EVCC Scheduler"** oder klicke **"+ Integration erstellen"**
3. Folge der Konfiguration:

   | Feld | Beispiel | Beschreibung |
   |------|----------|-------------|
   | **Host** | `192.168.1.100` | IP oder Hostname von EVCC |
   | **Port** | `7070` | EVCC API Port (Standard: 7070) |
   | **Token** | (leer) | Optional, falls EVCC Token-Auth hat |
   | **SSL** | An/Aus | HTTPS verwenden? (Standard: Aus) |
   | **Timeout** | `10` | HTTP Request Timeout in Sekunden |

4. Klicke **"Fertig"** und die Integration wird geladen

## Updates mit HACS

HACS kann die Integration automatisch updaten:

1. Gehe zu **HACS** → **Integrationen**
2. Suche nach **"EVCC Scheduler"**
3. Falls ein Update verfügbar ist, klicke **"Update"**
4. Nach dem Update: **Home Assistant neu starten**

## Troubleshooting

### Integration wird nicht angezeigt

- **Lösung 1**: Home Assistant-Cache löschen
  ```bash
  # SSH in Home Assistant
  ha core check  # Validiert die Integration
  ha core restart
  ```

- **Lösung 2**: Integration manuell validieren
  ```bash
  # Im Docker Container (falls vorhanden)
  python -m pytest custom_components/evcc_scheduler
  ```

### "Integration not found" Fehler

1. Überprüfe, dass die Repository-URL korrekt ist
2. Überprüfe, dass `manifest.json` vorhanden und gültig ist
3. Führe aus: `ha core check`

### WebSocket-Verbindung funktioniert nicht

1. Überprüfe, dass EVCC läuft: `ping <evcc-ip>`
2. Überprüfe Port: `curl http://<evcc-ip>:7070/api/state`
3. Prüfe die Logs:
   ```yaml
   logger:
     logs:
       evcc_scheduler: debug
   ```

## Deinstallation

Mit HACS:

1. Gehe zu **HACS** → **Integrationen**
2. Suche nach **"EVCC Scheduler"**
3. Klicke das **⋮ (Menü)-Symbol**
4. Wähle **"Deinstallieren"**
5. **Home Assistant neu starten**

## Support

- 📚 [Vollständige Dokumentation](DOCUMENTATION.md)
- 🐛 [Bug Reports](https://github.com/diestrohs/ha-evcc-scheduler/issues)
- 💬 [Diskussionen](https://github.com/diestrohs/ha-evcc-scheduler/discussions)

---

**HACS Integration Status**: ✅ Aktiv & getestet mit Home Assistant 2025.12
