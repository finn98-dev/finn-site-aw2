# OBS Studio — finndigital Setup
*Dispatch führt diese Konfiguration einmalig durch. Danach per Profil-Import übertragbar.*

---

## 1. Profil anlegen
`Profil → Neu → Name: "finndigital"`

---

## 2. Ausgabe-Einstellungen
`Einstellungen → Ausgabe → Modus: Erweitert`

**Aufnahme:**
| Einstellung | Wert |
|---|---|
| Format | MKV *(sicherer bei Absturz; nach Aufnahme zu MP4 umpacken)* |
| Encoder | H.264 (NVIDIA NVENC / Apple VT / x264 — je nach Hardware) |
| Qualitätsmodus | CRF / CQP |
| CRF-Wert | 18 *(hohe Qualität, große Datei — für Rohaufnahmen okay)* |
| Audio-Bitrate | 320 kbps |

**Audio-Spur:** `Spur 1 aktiv`, Rest deaktiviert.

---

## 3. Video-Einstellungen
`Einstellungen → Video`

| Einstellung | Wert |
|---|---|
| Basis-Auflösung | 1920 × 1080 |
| Ausgabe-Auflösung | 1920 × 1080 |
| FPS | 30 *(Kursvideos brauchen keine 60fps)* |
| Downscale-Filter | Lanczos |

---

## 4. Audio-Einstellungen
`Einstellungen → Audio`

| Einstellung | Wert |
|---|---|
| Abtastrate | 48 kHz |
| Kanal | Stereo |
| Desktop-Audio | Deaktiviert *(kein System-Sound in Aufnahme)* |
| Mikrofon / Hilfsgerät | Dein Mikrofon / Headset auswählen |

---

## 5. Szenen anlegen
`Szenen-Panel → + (Neu)`

### Szene 1: „Finn — Gesicht"
Quellen:
- `+ → Videoaufnahmegerät → Webcam auswählen`
- Auflösung: 1920 × 1080 oder native Kamera-Auflösung
- Filter auf Webcam-Quelle:
  - `Schärfen: 0.08`
  - `Farbkorrektur: Gamma 1.05, Sättigung 1.05` *(leicht wärmer)*

### Szene 2: „Finn — Bildschirm"
Quellen:
- `+ → Bildschirmaufnahme → Monitor auswählen`
- Auf 1920 × 1080 skalieren und zentrieren

### Szene 3: „Finn — Mix" *(Bildschirm + Kamera)*
Quellen (Reihenfolge = Ebenen, oben = vorne):
1. `Webcam` — positionieren: **unten links**, ca. 320 × 180px, mit rundem Rahmen
2. `Bildschirmaufnahme` — Vollbild

Webcam-Filter (nur in dieser Szene):
- Rechtsklick auf Webcam-Quelle → Filter:
  - `Farbkorrektur` (gleiche Werte wie Szene 1)
  - Optional: `Runden der Ecken` via LUT-Filter (Plugin "StreamFX" falls installiert)

---

## 6. Mikrofon-Filter
Rechtsklick auf Mikrofon-Quelle → Filter → hinzufügen:

| Filter | Einstellung |
|---|---|
| Rauschunterdrückung | RNNoise (empfohlen) oder Speex |
| Kompressor | Ratio: 4:1, Threshold: −18 dB, Attack: 10ms, Release: 60ms |
| Verstärker | Erst einstellen nach den anderen Filtern; Ziel: Peakmeter bei −6 bis −3 dB |

---

## 7. Hotkeys
`Einstellungen → Hotkeys`

| Aktion | Vorschlag |
|---|---|
| Aufnahme starten/stoppen | `F9` |
| Szene 1 (Gesicht) | `F1` |
| Szene 2 (Bildschirm) | `F2` |
| Szene 3 (Mix) | `F3` |
| Studio-Modus umschalten | `F12` |

---

## 8. Nach der Aufnahme: MKV → MP4 umpacken
OBS speichert in MKV. Umpacken (ohne Qualitätsverlust):

```bash
# In OBS: Datei → MKV-Aufnahmen in MP4 umwandeln
# ODER manuell:
ffmpeg -i aufnahme.mkv -c copy aufnahme.mp4
```

Danach die Datei in `video-production/` ablegen und mit `process.py` weiterbearbeiten.

---

## 9. Test-Checkliste vor der ersten echten Aufnahme
- [ ] Testaufnahme 30 Sekunden → Peakmeter, Qualität prüfen
- [ ] Bildschärfe der Webcam (manuelle Kamera-App, dann OBS-Feed prüfen)
- [ ] Kein Hall im Raum (Decke? Vorhänge hängen helfen)
- [ ] Beleuchtung: Licht **vor** dir, nicht hinter dir (kein Gegenlicht)
- [ ] Ton: Headset oder externes Mikrofon — Laptop-Mikrofon nicht verwenden
- [ ] Szenen-Wechsel mit Hotkeys testen
