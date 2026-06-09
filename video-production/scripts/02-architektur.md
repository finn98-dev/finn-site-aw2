# Video 02 — Wie ein KI-Agent wirklich funktioniert
**Track:** Bauen | **Typ:** Kostenlos | **Zieldauer:** ~14 min
**Status:** Skript fertig — Live-Demo-Block erst aufnehmen wenn Python-Loop stabil (JARVIS-5 Schritt 2+)

---

## Aufnahme-Hinweise
- Hauptteil: Szene „Finn — Gesicht"
- Architektur-Sektion: Szene „Finn — Bildschirm" (Gamma-Folie mit Diagramm)
- Demo-Block: Szene „Finn — Mix" (Telegram + Terminal nebeneinander)
- Demo-Block ist **separat aufnehmbar** und wird beim Schnitt eingefügt

### Gamma-Folie vorbereiten
Folie 1: Titelfolie „Wie ein KI-Agent wirklich funktioniert"
Folie 2: Zwei Spalten — „Chatbot" vs. „Agent"
Folie 3: Architektur-Diagramm (siehe unten)
Folie 4: Die 3 Schichten — einzeln erklärt
Folie 5: Warum kein Framework

---

## Skript

**[HOOK — 0:00 bis 0:50]**

Ich habe Jarvis dreimal neu gebaut.

Das erste Mal auf einem fertigen Framework — das irgendwann nicht mehr mit meinem API-Key funktioniert hat. Das zweite Mal direkt nach einem Serverabsturz, weil meine Festplatte vollgelaufen war. Und das dritte Mal — die Version, die heute läuft — in etwa zweihundert Zeilen Python.

Zweihundert Zeilen. Kein Framework. Kein Magie.

Wenn du verstehst, warum ich beim dritten Mal bei zweihundert Zeilen gelandet bin, verstehst du wie KI-Agenten wirklich funktionieren.

---

**[CHATBOT VS. AGENT — 0:50 bis 2:30]**
**[Bildschirm: Folie 2 — Zwei-Spalten-Vergleich]**

Lass uns kurz klären, was ein Agent überhaupt ist — weil das Wort gerade inflationär benutzt wird.

Wenn du ChatGPT öffnest und eine Frage schreibst, bekommst du eine Antwort. Das war's. Das Gespräch endet. Das Modell hat nichts getan — es hat Text produziert.

Ein Agent ist etwas anderes.

Ein Agent läuft in einer Schleife. Er empfängt eine Nachricht, denkt nach, entscheidet ob er etwas tun muss — und dann tut er es. Er ruft Kalender-APIs auf. Er schreibt Daten in eine Datenbank. Er schickt Befehle an Smart-Home-Geräte. Und dann antwortet er.

Das klingt simpel. Aber der Unterschied zwischen "Text ausgeben" und "Aktion ausführen" ist der Unterschied zwischen einem Taschenrechner und einem Mitarbeiter.

---

**[DIE DREI SCHICHTEN — 2:30 bis 5:30]**
**[Bildschirm: Folie 3 — Architektur-Diagramm]**

```
TELEGRAM
   ↓ Nachricht kommt rein
PYTHON AGENT LOOP
   ↓ sendet an
CLAUDE API (Opus)
   ↓ entscheidet über Tool-Calls
   ├── Destreamed  (Langzeitgedächtnis)
   ├── Google Calendar  (Termine)
   └── Smart Home  (SwitchBot / Hue)
   ↓ Antwort
TELEGRAM
```

Drei Schichten — mehr ist es nicht.

**Schicht 1: Der Eingang.** Bei mir ist das Telegram. Ich schreibe eine Nachricht — Jarvis empfängt sie. Du könntest hier auch E-Mail nehmen, eine Slack-Nachricht, oder einen Cron-Job der automatisch auslöst.

**Schicht 2: Das Gehirn.** Das ist Claude — das Sprachmodell von Anthropic. Ich nutze Opus, weil es am besten darin ist, Aufgaben zu verstehen und Entscheidungen zu treffen. Claude liest meine Nachricht und entscheidet: brauche ich dafür ein Tool? Welches? Mit welchen Parametern?

Das nennt sich Tool-Calling. Ich definiere vorab, welche Tools Jarvis hat — mit einer Beschreibung was jedes Tool tut. Claude wählt selbst aus welches es braucht.

**Schicht 3: Die Tools.** Das ist der Teil, der die echte Arbeit macht. Destreamed ist mein Langzeitgedächtnis — alles was Jarvis über mich wissen soll, liegt da drin. Google Calendar für Termine. SwitchBot und Philips Hue für das Smart Home.

---

**[WARUM KEIN FRAMEWORK — 5:30 bis 7:30]**
**[Bildschirm: Folie 5 — zurück zur Kamera wechseln]**

Ich habe vorhin gesagt, ich habe dreimal angefangen. Lass mich kurz erklären, warum.

Beim ersten Mal habe ich OpenClaw benutzt — ein fertiges Framework das viele dieser Schichten für dich abstrahiert. Fertig installiert, schöne Oberfläche, Grafana-Dashboard für Monitoring, Traefik als Reverse Proxy — alles dabei.

Das Problem: Als ich auf API-Key-Basis umgestellt habe — statt Claude Pro — hat OpenClaw aufgehört zu funktionieren. Framework-Bug, nicht mein Fehler, keine schnelle Lösung. Dann hatte ich noch einen Disk-Full-Crash durch eine Ollama-Installation die alles vollgeschrieben hat. Und dann war ich ausgesperrt vom Server.

Drei Probleme, drei Wochen verloren.

Beim dritten Anlauf habe ich beschlossen: Ich schreibe das selbst. Kleiner Python-Loop, Telegram Long-Polling, direkter API-Call an Claude, Tool-Definitionen als Python-Dictionaries.

Zweihundert Zeilen. Jede davon verstehe ich. Wenn etwas bricht, weiß ich wo ich hinschauen muss.

Das ist die wichtigste Lektion aus diesem Projekt — nicht welches Framework du benutzt, sondern dass du verstehst was unter der Haube passiert.

---

**[LIVE-DEMO — 7:30 bis 9:30]**
**⚠️ SEPARATER AUFNAHME-BLOCK — erst wenn JARVIS-5 Schritt 2+ fertig**
**[Szene: Mix — Telegram links, Terminal rechts]**

Lass mich dir zeigen wie das konkret aussieht.

Ich schreibe Jarvis: *„Was steht heute an?"*

**[Nachricht absenden, warten]**

Im Terminal siehst du die Schleife — die Nachricht kommt rein, Claude wird aufgerufen, die Tool-Calls laufen durch — Destreamed wird abgefragt, Calendar wird gelesen — und dann kommt die Antwort zurück.

**[Auf Antwort zeigen]**

Das ist kein Chatbot. Das ist ein System das aktiv Informationen zieht, kombiniert und eine Entscheidung trifft.

Und das läuft auf einem Hetzner-Server in Frankfurt. 24 Stunden am Tag. Acht Euro im Monat.

---

**[ABSCHLUSS & CTA — 9:30 bis 10:30]**

Wenn du bis hierher geschaut hast, weißt du jetzt wie ein KI-Agent aufgebaut ist.

Was du noch nicht weißt: wie du das selbst baust.

In den nächsten drei Videos — die du mit einmaligen 34 Euro freischaltest — setzen wir das auf. Du richtest die Entwicklungsumgebung ein. Du bekommst deinen eigenen Claude-API-Key. Du schreibst Schicht für Schicht diesen Agent-Loop — mit meinem Code als Vorlage, aber so dass du jede Zeile verstehst.

Am Ende von Video fünf läuft dein Agent auf einem echten Server. Nicht lokal, nicht in einer Demo — live.

Und du bekommst deinen Badge.

Bereit?

**[Kurze Pause, direkter Blick in die Kamera]**

Dann geht's los.

---

## Schnitt-Hinweise (nach Aufnahme ausfüllen)
- Hook-Start: `__:__`
- Bildschirm-Wechsel zu Folie: `__:__`
- Zurück zur Kamera: `__:__`
- Demo-Block einfügen nach: `__:__`
- Demo-Block Ende: `__:__`
- Abschluss-Start: `__:__`
- Segment-Cuts (Versprecher etc.): _____
