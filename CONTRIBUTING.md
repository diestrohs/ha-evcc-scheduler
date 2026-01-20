# Beiträge zu EVCC Scheduler

Danke für dein Interesse, zum EVCC Scheduler Projekt beizutragen!

## Code von Conduct

Dieses Projekt und alle Teilnehmer unterliegen unserem [Code of Conduct](CODE_OF_CONDUCT.md). Durch die Teilnahme bestätigst du, dass du diesen Code einhalten wirst.

## Wie kann ich beitragen?

### Fehler berichten

Fehlerberichte sind sehr wertvoll! Bitte verwende GitHub Issues mit folgendem Format:

```
**Beschreibung des Fehlers**
Eine kurze Beschreibung

**Zu reproduzierende Schritte**
1. ...
2. ...

**Erwartetes Verhalten**
Was sollte passieren?

**Aktuelles Verhalten**
Was passiert tatsächlich?

**Umgebung**
- Home Assistant Version: 2025.12
- EVCC Version: 0.210.2
- Python Version: 3.12
- Logs: (Bitte Debug-Logs hinzufügen)
```

### Features vorschlagen

Feature-Anfragen sind auch willkommen! Erstelle ein Issue mit:

```
**Ist dies ein Feature-Request?**
Ja

**Beschreibung**
Was möchtest du erreichen?

**Begründung**
Warum ist dieses Feature wichtig?

**Mögliche Implementierung**
Wie könnten wir das implementieren?

**Alternnativen**
Gibt es andere Lösungen?
```

### Pull Requests

1. **Fork** das Repository
2. **Clone** dein Fork lokal
3. **Erstelle einen Branch**: `git checkout -b feature/deine-funktion`
4. **Committe deine Änderungen**: `git commit -am 'Add deine Funktion'`
5. **Push** zum Branch: `git push origin feature/deine-funktion`
6. **Öffne einen Pull Request**

#### Pull Request Checklist

- [ ] Code folgt dem Projekt-Style (PEP 8)
- [ ] Alle Funktionen haben Type-Hints
- [ ] Logging ist hinzugefügt (debug-Level)
- [ ] Dokumentation ist aktualisiert
- [ ] Tests sind vorhanden und bestanden
- [ ] Keine Breaking Changes ohne Dokumentation
- [ ] Commit-Nachrichten sind aussagekräftig

### Entwicklung

**Entwicklungs-Setup:**

```bash
git clone https://github.com/diestrohs/ha-evcc-scheduler.git
cd evcc_scheduler
pip install -e .
```

**Code-Style:**

- Python: PEP 8
- Line Length: 120 Zeichen
- Type Hints: Für alle Funktionen erforderlich
- Imports: Standard → Drittparteien → Home Assistant → Lokal

**Linting:**

```bash
pip install flake8
flake8 . --max-line-length=120
```

### Dokumentation

- Aktualisiere `DOCUMENTATION.md` für technische Änderungen
- Aktualisiere `README.md` für Nutzer-sichtbare Änderungen
- Verwende Markdown mit korrektem Formatting
- Füge Beispiele hinzu wo relevant

### Versions-Verwaltung

Wir folgen [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking Changes
- **MINOR**: Neue Features (rückwärtskompatibel)
- **PATCH**: Bug-Fixes

Update `manifest.json` `version` Feld bei Releases.

## Fragen?

- 📚 Lese die [DOCUMENTATION.md](DOCUMENTATION.md)
- 💬 Öffne eine [Discussion](https://github.com/diestrohs/ha-evcc-scheduler/discussions)
- 📧 Kontaktiere die Maintainer

## Lizenz

Durch Beiträge zu diesem Projekt stimmst du zu, dass deine Beiträge unter der MIT Lizenz lizenziert werden.

---

Danke für deinen Beitrag! 🎉
