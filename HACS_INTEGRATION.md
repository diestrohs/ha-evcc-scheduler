# HACS Integration Guide

## HACS Kompatibilität ✅

Diese Integration ist vollständig HACS-kompatibel und erfüllt alle Anforderungen von [HACS Publishing Guidelines](https://www.hacs.xyz/docs/publish/start/).

### Erfüllte HACS-Anforderungen

| Anforderung | Status | Details |
|---|---|---|
| **Repository-Struktur** | ✅ | `custom_components/evcc_scheduler/` mit allen Dateien |
| **manifest.json** | ✅ | Alle erforderlichen Felder: `domain`, `documentation`, `issue_tracker`, `codeowners`, `name`, `version` |
| **hacs.json** | ✅ | Root-Datei mit Integration-Metadaten |
| **README** | ✅ | Umfangreiche Dokumentation mit Installation & Nutzung |
| **Lizenz** | ✅ | MIT License vorhanden |
| **Home Assistant Brands** | ℹ️ | Optional für Standard-Repositories (wird für public/custom geleitet) |

### Erforderliche Felder im Manifest

```json
{
  "domain": "evcc_scheduler",
  "name": "EVCC Scheduler",
  "version": "0.0.4",
  "documentation": "https://github.com/yourusername/evcc_scheduler",
  "issue_tracker": "https://github.com/yourusername/evcc_scheduler/issues",
  "codeowners": ["@yourusername"],
  "homeassistant": "2025.12.0"
}
```

### hacs.json Konfiguration

```json
{
  "name": "EVCC Scheduler",
  "homeassistant": "2025.12.0",
  "hacs": "2.0.0",
  "documentation": "https://github.com/yourusername/evcc_scheduler",
  "issue_tracker": "https://github.com/yourusername/evcc_scheduler/issues"
}
```

## Installation via HACS

### 1. Custom Repository hinzufügen

```
HACS → Integrationen → ⋮ Menü → Custom Repositories
→ Repository URL: https://github.com/yourusername/evcc_scheduler
→ Kategorie: Integration
→ Erstellen
```

### 2. Integration installieren

```
HACS → Integrationen → EVCC Scheduler
→ Installieren
→ Home Assistant neu starten ⭐ WICHTIG
```

### 3. Konfiguration hinzufügen

```
Einstellungen → Geräte und Services → + Integration erstellen
→ EVCC Scheduler
→ Host, Port, Token (optional) eingeben
→ Speichern
```

## Checkliste für HACS Default Repository

Wenn Sie diese Integration zum HACS Default Repository hinzufügen möchten:

- [ ] **Repository**: Public auf GitHub
- [ ] **Description**: Im GitHub-Repository gesetzt (2-3 Sätze)
- [ ] **Topics**: GitHub Topics hinzugefügt: `homeassistant`, `integration`, `evcc`, `ev-charging`
- [ ] **Releases**: GitHub Releases veröffentlicht (Tags reichen nicht!)
  - [ ] Semantische Versionierung (z.B. `0.0.4`)
  - [ ] Release Notes mit Changelog
  - [ ] ≥5 Releases empfohlen für HACS-Store-Präsenz
- [ ] **Home Assistant Brands**: Integration in [home-assistant/brands](https://github.com/home-assistant/brands) registriert (optional, aber empfohlen für UI-Konsistenz)
- [ ] **Code-Qualität**: 
  - [ ] Type-Hints für alle Funktionen
  - [ ] Logging auf DEBUG-Level
  - [ ] Fehlerbehandlung mit aussagekräftigen Messages
- [ ] **Dokumentation**: 
  - [ ] README mit Installation, Nutzung, Konfiguration
  - [ ] Links zu Documentation & Issue Tracker im manifest.json
  - [ ] Lovelace-Card-Support dokumentiert (optional)

### Home Assistant Brands Registrierung

Falls Sie später ins HACS Default Repository möchten, müssen Sie die Integration in `home-assistant/brands` registrieren:

1. Fork: https://github.com/home-assistant/brands
2. Folder erstellen: `custom_integrations/evcc_scheduler/`
3. Datei hinzufügen: `icon.png` oder `icon.svg` + `icon@2x.png` (optional)
4. Pull Request an home-assistant/brands

Beispiel-Struktur:
```
custom_integrations/
  evcc_scheduler/
    icon.png (512x512)
    icon@2x.png (1024x1024) [optional]
```

## GitHub Releases

Für HACS ist das Veröffentlichen von Releases nicht zwingend erforderlich, wird aber **empfohlen**:

### Release erstellen

1. GitHub → Releases → Create a new release
2. Tag: `0.0.4` (muss mit `version` in manifest.json übereinstimmen)
3. Title: `Release 0.0.4`
4. Description: 
   ```markdown
   ## What's new in 0.0.4

   ### Features
   - Entity-ID simplified to be vehicle-agnostic
   - Entity manager optimized for minimal registry access
   - Vehicle metadata added to switch attributes

   ### Fixes
   - Toggle service removed (use `active` field in set_repeating_plan)

   ### Documentation
   - Comprehensive German & English documentation
   - HACS compatibility verified
   ```
5. Publish release

### Vorteil für HACS-Nutzer

Mit Releases erhält der HACS-Nutzer eine schöne Auswahl der letzten 5 Releases + Standard Branch.

## Troubleshooting

### "Integration nicht im HACS Store"
- ✅ Custom Repository URL hinzufügen (s.o.)
- ✅ Für Default Store: Anfrage an [HACS Include](https://www.hacs.xyz/docs/publish/include/) stellen

### "manifest.json ungültig"
- Prüfen: Alle erforderlichen Felder vorhanden?
- Felder: `domain`, `documentation`, `issue_tracker`, `codeowners`, `name`, `version`
- JSON-Validierung: https://jsonlint.com/

### "hacs.json nicht erkannt"
- Muss im Repository-Root sein (nicht in custom_components/evcc_scheduler/)
- Korrekte Feldnamen: `name`, `homeassistant`, `issue_tracker` (nicht `issuetracker`!)

### "Version stimmt nicht überein"
- manifest.json `version`: `0.0.4`
- GitHub Release Tag: `0.0.4` (exakt gleich)
- hacs.json: Keine Version nötig (kommt aus manifest.json)

## Weitere Ressourcen

- [HACS Publishing Guidelines](https://www.hacs.xyz/docs/publish/start/)
- [Integration Requirements](https://www.hacs.xyz/docs/publish/integration/)
- [Home Assistant Integration Manifest](https://developers.home-assistant.io/docs/creating_integration_manifest)
- [HACS Default Repository](https://www.hacs.xyz/docs/publish/include/)

## Kontakt & Support

- **GitHub Issues**: https://github.com/yourusername/evcc_scheduler/issues
- **Discord**: HACS Community im [Home Assistant Discord](https://discord.gg/home-assistant)

---

**Status**: ✅ HACS-kompatibel (Custom Repository ready)  
**Aktualisiert**: Januar 2026
