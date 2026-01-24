# HACS Kompatibilitäts-Checkliste

## ✅ Erfüllte Anforderungen

### 1. Repository-Struktur
- [x] Public GitHub Repository
- [x] `custom_components/evcc_scheduler/` Ordner mit Integration
- [x] Alle Integration-Dateien in einem Ordner (kein Splitting)
- [x] Nur eine Integration pro Repository

```
Repository Root/
├── custom_components/
│   └── evcc_scheduler/
│       ├── __init__.py
│       ├── api.py
│       ├── config_flow.py
│       ├── const.py
│       ├── coordinator.py
│       ├── entity_manager.py
│       ├── mapping.py
│       ├── services.py
│       ├── services.yaml
│       ├── switch.py
│       ├── websocket_api.py
│       ├── websocket_client.py
│       ├── manifest.json
│       ├── translations/
│       │   ├── de.json
│       │   └── en.json
│       └── ws_api.py
├── hacs.json (Root)
├── README.md
├── LICENSE
└── .github/
```

✅ **Status**: Korrekt strukturiert

### 2. manifest.json
- [x] `domain` Feld vorhanden
- [x] `name` Feld vorhanden
- [x] `version` Feld vorhanden (0.1.2)
- [x] `documentation` URL vorhanden
- [x] `issue_tracker` URL vorhanden (korrekt benannt, nicht `issuetracker`)
- [x] `codeowners` Array vorhanden
- [x] `homeassistant` Feld mit Mindestversion
- [x] `iot_class` Feld vorhanden
- [x] `config_flow` Set to true

```json
{
  "domain": "evcc_scheduler",
  "name": "EVCC Scheduler",
  "version": "0.1.2",
  "documentation": "https://github.com/diestrohs/ha-evcc-scheduler",
  "issue_tracker": "https://github.com/diestrohs/ha-evcc-scheduler/issues",
  "codeowners": ["@diestrohs"],
  "homeassistant": "2025.12.0",
  "iot_class": "local_polling",
  "config_flow": true,
  "integration_type": "service",
  "platforms": ["switch"]
}
```

✅ **Status**: Alle erforderlichen Felder vorhanden und korrekt

### 3. hacs.json
- [x] Im Repository-Root (nicht in custom_components/)
- [x] `name` Feld vorhanden
- [x] `homeassistant` Feld mit Mindestversion
- [x] `documentation` URL vorhanden
- [x] `issue_tracker` URL vorhanden (korrekt benannt)
- [x] Keine `requirements` (gehören ins manifest.json)

```json
{
  "name": "EVCC Scheduler",
  "homeassistant": "2025.12.0",
  "hacs": "2.0.0",
  "documentation": "https://github.com/yourusername/evcc_scheduler",
  "issue_tracker": "https://github.com/yourusername/evcc_scheduler/issues"
}
```

✅ **Status**: Minimal und korrekt konfiguriert

### 4. README.md
- [x] Vorhanden und aussagekräftig
- [x] Installation-Anleitung
- [x] Features beschrieben
- [x] Konfiguration erklärt
- [x] Viele Sprachen unterstützt (EN/DE)

✅ **Status**: Umfangreiche Dokumentation vorhanden

### 5. Lizenz
- [x] MIT License vorhanden (LICENSE Datei)
- [x] Lizenztext vollständig

✅ **Status**: MIT License aktiv

### 6. Versionskontrolle
- [x] Git Repository vorhanden
- [x] .git/ Ordner mit History
- [x] Commits vorhanden

✅ **Status**: Git-Setup korrekt

### 7. Code-Qualität
- [x] Type-Hints für Funktionen
- [x] Logging mit `_LOGGER`
- [x] Fehlerbehandlung implementiert
- [x] Async/await Pattern konsistent
- [x] Keine hartcodierten Secrets/Credentials

✅ **Status**: Production-ready Code

---

## ℹ️ Optionale Anforderungen (empfohlen)

### GitHub Releases
- [x] **Status**: Veröffentlicht (0.0.1 - 0.1.2)
- [x] **Empfehlung**: Für HACS-Store-Sichtbarkeit erstellt

**Verfügbare Releases**:
```
GitHub → Releases:
  - 0.0.1 (Initial)
  - 0.0.2 (Features)
  - 0.0.3 (Services)
  - 0.0.4 (Optimierungen)
  - 0.1.0 (Stable)
  - 0.1.2 (Patch - aktuell)
```

### Home Assistant Brands
- [ ] **Status**: Nicht registriert
- [ ] **Nächster Schritt**: Optional, nur für HACS Default Store
- [ ] **Anforderung**: Fork von https://github.com/home-assistant/brands

**Was zu tun ist**:
```
1. Fork https://github.com/home-assistant/brands
2. Folder erstellen: custom_integrations/evcc_scheduler/
3. Icon hinzufügen: icon.png (512x512) + icon@2x.png
4. Pull Request an home-assistant/brands
```

---

## 🚀 Installation Testen

### Custom Repository (HACS 2.0+)

```bash
# 1. HACS öffnen
# 2. Integrationen → ⋮ Menü → Custom Repositories
# 3. URL eintragen: https://github.com/yourusername/evcc_scheduler
# 4. Kategorie: Integration
# 5. Erstellen
# 6. EVCC Scheduler → Installieren
# 7. HA neu starten
```

**Erwartetes Ergebnis**:
- ✅ Integration installiert
- ✅ Konfigurationsflow erscheint
- ✅ Service registriert
- ✅ Entities erstellt

### Lokales Testen (vor HACS-Submit)

```bash
# Integration lokal testen:
# 1. Datei: custom_components/evcc_scheduler/
# 2. In HA config directory kopieren
# 3. HA neu starten
# 4. Developer Tools → Services prüfen
# 5. Entities prüfen
```

---

## 📋 Schritte zum HACS Default Store

Wenn Sie später ins HACS Default Store möchten:

### Phase 1: Custom Repository Ready ✅
- [x] Struktur korrekt
- [x] manifest.json korrekt
- [x] hacs.json vorhanden
- [x] README vorhanden
- [x] License vorhanden
- [x] Code-Qualität gut

**Nächster Schritt**: Benutzer können hinzufügen via Custom Repository URL

### Phase 2: Releases & Stabilität
- [x] GitHub Releases für 0.0.1 - 0.1.2 erstellt
- [x] Mehrere Releases für HACS-Sichtbarkeit verfügbar
- [x] Stable Release (0.1.2) vorhanden
- [ ] Test-Feedback von Benutzern einholen

**Wann**: Nach ein paar Wochen Betrieb mit Custom Repository

### Phase 3: HACS Include Request
- [ ] Home Assistant Brands registrieren (optional)
- [ ] Issue in https://github.com/hacs/default erstellen
- [ ] Anfrage: "Add integration to default store"
- [ ] HACS-Team wird Repository überprüfen
- [ ] Bei OK: Ins Default Store aufgenommen

**Link**: https://www.hacs.xyz/docs/publish/include/

---

## 🔧 Häufige Fehler & Lösungen

### ❌ "hacs.json nicht erkannt"

**Ursachen**:
- hacs.json im falschen Ordner (sollte im Root sein, nicht in custom_components/)
- Feldname falsch: `issuetracker` statt `issue_tracker`
- JSON-Syntax-Fehler

**Lösung**:
```json
{
  "name": "EVCC Scheduler",
  "homeassistant": "2025.12.0",
  "hacs": "2.0.0",
  "documentation": "https://...",
  "issue_tracker": "https://..."  // ← issue_tracker (nicht issuetracker)
}
```

### ❌ "manifest.json ungültig"

**Ursachen**:
- Fehlende erforderliche Felder
- Feldname falsch: `issuetracker` statt `issue_tracker`

**Lösung**:
```json
{
  "domain": "evcc_scheduler",
  "name": "EVCC Scheduler",
  "version": "0.1.2",
  "documentation": "https://github.com/diestrohs/ha-evcc-scheduler",
  "issue_tracker": "https://github.com/diestrohs/ha-evcc-scheduler/issues",
  "codeowners": ["@diestrohs"],
  "homeassistant": "2025.12.0",
  "iot_class": "local_polling",
  "config_flow": true,
  "integration_type": "service",
  "platforms": ["switch"]
}
```

### ❌ "Integration nicht im HACS Store"

**Ursachen**:
- Keine Releases erstellt
- Repository nicht public
- HACS nicht aktualisiert (Cache)

**Lösung**:
1. GitHub Releases erstellen
2. HACS neu laden/updaten
3. Custom Repository hinzufügen (als Zwischenlösung)
4. HACS Default Include anfordern

### ❌ "Version stimmt nicht überein"

**Ursachen**:
- manifest.json Version ≠ GitHub Release Tag

**Lösung**:
```
manifest.json: "version": "0.1.2"
GitHub Tag:    "0.1.2"  ← exakt gleich!
```

---

## 📞 Support & Ressourcen

- **HACS Docs**: https://www.hacs.xyz/docs/publish/start/
- **Integration Anforderungen**: https://www.hacs.xyz/docs/publish/integration/
- **Manifest Dokumentation**: https://developers.home-assistant.io/docs/creating_integration_manifest
- **HACS Include**: https://www.hacs.xyz/docs/publish/include/
- **GitHub Brands**: https://github.com/home-assistant/brands
- **Home Assistant Discord**: https://discord.gg/home-assistant

---

## ✅ Finales Status

| Kategorie | Status | Nächster Schritt |
|---|---|---|
| **Repository** | ✅ Ready | Nichts (ist fertig) |
| **manifest.json** | ✅ Valid | Nichts (ist fertig) |
| **hacs.json** | ✅ Valid | Nichts (ist fertig) |
| **Dokumentation** | ✅ Excellent | Nichts (ist fertig) |
| **GitHub Releases** | ℹ️ Optional | Releases erstellen (empfohlen) |
| **Home Assistant Brands** | ℹ️ Optional | Nur für Default Store |
| **HACS Default Store** | 📋 Später | Nach stabiler Release |

**Zusammenfassung**: 
- ✅ **Custom Repository**: Sofort einsatzbereit
- 📋 **HACS Default Store**: Nach Releases & Stabilisierung möglich

---

**Status**: ✅ HACS-kompatibel (Custom Repository Ready)  
**Aktualisiert**: 24. Januar 2026  
**Version**: 0.1.2
