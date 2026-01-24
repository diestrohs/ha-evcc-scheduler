# GitHub Releases & Versioning Guide

## Semantische Versionierung (SemVer)

Diese Integration folgt **Semantic Versioning 2.0.0**:

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking Changes (z.B. API-Änderungen, HA-Anforderungen erhöht)
- **MINOR**: Neue Features (abwärtskompatibel)
- **PATCH**: Bugfixes (keine neuen Features)

### Aktuelle Version

```
0.1.0
└─ First stable (0.x)
```

## Version Roadmap

| Version | Status | Merkmale |
|---|---|---|
| 0.0.1 | ✅ Veröffentlicht | Initial Release, Basis-Features |
| 0.0.2 | ✅ Veröffentlicht | WebSocket-Unterstützung, Entity Manager |
| 0.0.3 | ✅ Veröffentlicht | Services (set/del), Fehlerbehandlung |
| 0.0.4 | ✅ Veröffentlicht | Entity-ID Vereinfachung, Optimierungen |
| 0.0.5 | ✅ Veröffentlicht | HACS Default Store, Home Assistant Brands |
| 0.1.0 | ✅ Veröffentlicht | Stable Release, WS/Polling Konfiguration, WS API |

## Release-Prozess

### 1. Vorbereitung

Vor jedem Release:

```bash
# 1. Changelog/Notizen sammeln
# 2. Tests durchführen:
#    - Integration in HA 2025.12 installieren
#    - Alle Services testen
#    - Fahrzeugwechsel testen
#    - WebSocket & Polling testen
# 3. Versionen synchronisieren:

# manifest.json updaten
{
  "version": "0.1.0"
}

# hacs.json hat keine Version (kommt aus manifest.json)
```

### 2. GitHub Release erstellen

**Via GitHub Web UI**:

1. Repository → Releases → Draft a new release
2. **Tag**: `0.1.0` (exakt mit manifest.json)
3. **Target**: `master` (default branch)
4. **Title**: `Release 0.1.0`
5. **Description**: (s. Beispiel unten)
6. **Options**:
   - [ ] This is a pre-release (nur für Beta-Versionen)
   - [ ] Create a discussion (optional)
7. **Publish**

**Via Git CLI**:

```bash
git tag 0.1.0
git push origin 0.1.0
# Dann Release auf GitHub UI erstellen mit Notes
```

### 3. Release-Notes Vorlage

```markdown
## 🎉 Release 0.1.0

### What's new?

#### ✨ Features
- Feature 1
- Feature 2

#### 🐛 Fixes
- Bug fix 1
- Bug fix 2

#### 📚 Documentation
- Documentation updates
- New guides

#### ⚡ Performance
- Performance improvement 1
- Optimization 2

### 🔄 Dependencies

- Home Assistant: 2025.12.0+
- EVCC: 0.210.2+
- Python: 3.11+
- aiohttp: 3.8.0+

### 📝 Installation

```
HACS → Integrationen → EVCC Scheduler → Aktualisieren
```

### 🙏 Credits

Thanks to:
- Contributors
- Testers
- EVCC team

### 📦 Files Changed

- `manifest.json`: Version bumped
- `entity_manager.py`: Performance improvements
- `DOCUMENTATION.md`: Updated examples
- Plus weitere...
```

## Release-Notes für aktuelle Version (0.1.0)

```markdown
## 🎉 Release 0.1.0

### What's new?

#### ✨ Features
- Konfigurierbarer WebSocket- vs. Polling-Modus inkl. Poll-Intervall (Default: 30s)
- WebSocket API für die Custom Lovelace Card (`scheduler/get|add|edit|deleate`)
- Switch-Attribute enthalten Fahrzeug-Metadaten (`vehicle_title`, `vehicle_id`)
- Entity-Lifecycle optimiert: `update_data()` aktualisiert Entities ohne Registry-Churn

#### 🐛 Fixes
- Plan-Erstellung: `build_entity_id()` Signatur korrigiert, Pläne werden sauber angelegt
- Plan-Toggle: Holt aktuelle EVCC-Pläne vor dem Schreiben (keine veralteten Arrays)
- Entity-Namen vereinheitlicht (`evcc_repeating_plan_{index}`)

#### 📚 Documentation
- Deutsche und englische Dokumentation aktualisiert
- Release- und Architektur-Guides aufgefrischt

#### ⚡ Performance
- Entity Manager: Registry nur bei Löschungen geladen (lazy)
- WebSocket-Updates dedupliziert, häufig ohne zusätzliche API-Calls

### 🔄 Dependencies

- Home Assistant: 2025.12.0+
- EVCC: 0.210.2+
- Python: 3.11+
- aiohttp: 3.8.0+

### 🔄 Breaking Changes

- Keine. Entity-IDs bleiben stabil (`evcc_repeating_plan_{index}`).

### 📝 Installation

```
HACS → Integrationen → EVCC Scheduler
→ Benutzerdefinierte Repositories
→ https://github.com/yourusername/evcc_scheduler
→ Installieren → Home Assistant neu starten
```

### 📋 Checkliste nach Update

- [ ] Home Assistant neu gestartet
- [ ] WebSocket-Updates werden empfangen (oder Polling-Fallback getestet)
- [ ] Fahrzeugwechsel getestet (Entities bleiben stabil)
- [ ] Services `set_repeating_plan` / `del_repeating_plan` funktionieren
- [ ] Custom Card (falls genutzt) erhält `scheduler/*` Antworten

### 🙏 Credits

Vielen Dank an:
- Home Assistant Community
- EVCC Team & Community
- Beta-Tester

### 📝 Bekannte Probleme

Keine bekannten Probleme in dieser Version.

### 🔮 Next Steps

- Version 0.1.1: Bugfixes & HACS Review Tasks
- Version 0.2.0: Erweiterte Scheduling-Features / Templates
```

## Automatisierte Release-Prozesse (Optional)

### GitHub Actions für automatische Releases

```yaml
# .github/workflows/release.yml
name: Create Release

on:
  push:
    tags:
      - "*"

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body: |
            Release notes here
          draft: false
          prerelease: false
```

## Version-Synchronisierung checken

Skript zum Prüfen, ob alle Versionen synchron sind:

```bash
#!/bin/bash
# check_versions.sh

MANIFEST_VERSION=$(grep '"version"' manifest.json | sed 's/.*"\([^"]*\)".*/\1/')
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")

echo "manifest.json version: $MANIFEST_VERSION"
echo "Latest git tag: $LATEST_TAG"

if [ "$MANIFEST_VERSION" = "$LATEST_TAG" ]; then
    echo "✅ Versionen synchron"
else
    echo "❌ Versionen unterschiedlich!"
    echo "   → manifest.json aktualisieren: $MANIFEST_VERSION"
    echo "   → Git tag erstellen: git tag $MANIFEST_VERSION"
fi
```

## Langfristige Versionsplanung

```
0.0.x Phase (Pre-Release)
  ├─ 0.0.1-0.0.4: Feature-Development
  ├─ Focus: API-Stabilität, Core-Features
  └─ Breaking Changes möglich (kommuniziert)

0.1.0 Phase (First Stable)
  ├─ Stable API versprochen
  ├─ HACS Default Store ready
  └─ Semver eingehalten (keine Breaking Changes ohne Major)

0.2.0+ Phase (Maintenance)
  ├─ Bug Fixes (PATCH)
  ├─ Neue Features (MINOR)
  └─ Großere Refactorings (MAJOR)
```

## Checkliste für neues Release

- [ ] Changelog aktualisiert (CHANGELOG.md oder Release Notes)
- [ ] manifest.json version aktualisiert
- [ ] Alle Code-Changes committed
- [ ] Git Tag erstellt: `git tag X.X.X`
- [ ] Git Push mit Tags: `git push origin master --tags`
- [ ] GitHub Release Draft erstellt
- [ ] Release Notes aktualisiert
- [ ] Veröffentlicht
- [ ] HACS-Store automatisch aktualisiert wird (mit Verzögerung)

---

**Letzte Aktualisierung**: Januar 2026  
**Aktuelle Version**: 0.1.0
