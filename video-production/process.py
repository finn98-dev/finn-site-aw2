#!/usr/bin/env python3
"""
finndigital Video-Prozessor
Automatisierte Nachbearbeitung von Rohaufnahmen via FFmpeg.

Verwendung:
  python3 process.py normalize  input.mp4 working.mp4
  python3 process.py silence    input.mp4 no-silence.mp4
  python3 process.py cut        input.mp4 output.mp4  "0:30-3:45,4:00-8:30"
  python3 process.py finalize   input.mp4 final.mp4
  python3 process.py auto       input.mp4 final.mp4          ← alles in einem Schritt

Voraussetzung: ffmpeg installiert (brew install ffmpeg / apt install ffmpeg)
"""

import subprocess
import sys
import os
import re
import tempfile
import shutil
from pathlib import Path


# ── Farben für Terminal-Output ──────────────────────────────────────────────
G = "\033[32m"  # grün
Y = "\033[33m"  # gelb
R = "\033[31m"  # rot
B = "\033[34m"  # blau
X = "\033[0m"   # reset


def info(msg):  print(f"{B}→{X} {msg}")
def ok(msg):    print(f"{G}✓{X} {msg}")
def warn(msg):  print(f"{Y}⚠{X} {msg}")
def err(msg):   print(f"{R}✗{X} {msg}"); sys.exit(1)


def require_ffmpeg():
    if not shutil.which("ffmpeg"):
        err("FFmpeg nicht gefunden. Installieren: brew install ffmpeg / apt install ffmpeg")


def run(cmd, quiet=False):
    """FFmpeg-Befehl ausführen, Fehler abfangen."""
    if not quiet:
        info(" ".join(str(c) for c in cmd[:6]) + " ...")
    result = subprocess.run(
        [str(c) for c in cmd],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        err(f"FFmpeg-Fehler:\n{result.stderr[-800:]}")
    return result


def get_duration(src):
    """Videolänge in Sekunden ermitteln."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", str(src)],
        capture_output=True, text=True
    )
    import json
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


# ── Schritt 1: Audio normalisieren ─────────────────────────────────────────
def normalize(src, dst):
    """
    Normalisiert Audio auf -16 LUFS (Standard für Teachable / YouTube).
    Zweistufig: erst analysieren, dann rendern.
    """
    info(f"Normalisiere Audio: {src}")

    # Analyse-Pass
    analysis = subprocess.run(
        ["ffmpeg", "-i", str(src),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True
    )
    # Gemessene Werte aus stderr extrahieren
    stderr = analysis.stderr
    match = re.search(r'\{[^}]*"input_i"[^}]*\}', stderr, re.DOTALL)

    if match:
        import json
        loud_data = json.loads(match.group(0))
        af = (
            f"loudnorm=I=-16:TP=-1.5:LRA=11"
            f":measured_I={loud_data['input_i']}"
            f":measured_LRA={loud_data['input_lra']}"
            f":measured_TP={loud_data['input_tp']}"
            f":measured_thresh={loud_data['input_thresh']}"
            f":linear=true:print_format=summary"
        )
    else:
        warn("Analyse-Pass fehlgeschlagen, nutze einfache Normalisierung.")
        af = "loudnorm=I=-16:TP=-1.5:LRA=11"

    run(["ffmpeg", "-i", src,
         "-af", af,
         "-c:v", "copy",
         dst, "-y"])
    ok(f"Audio normalisiert → {dst}")


# ── Schritt 2: Stille entfernen ─────────────────────────────────────────────
def remove_silence(src, dst, threshold_db=-35, min_duration=1.2):
    """
    Pausen länger als min_duration Sekunden werden entfernt.
    threshold_db: alles unter diesem Pegel gilt als Stille (-35 dB = leises Rauschen)
    min_duration: Mindestlänge einer Pause in Sekunden (1.2s = Standardpause zwischen Sätzen)
    """
    info(f"Entferne Pausen >{min_duration}s unter {threshold_db}dB: {src}")
    run(["ffmpeg", "-i", src,
         "-af", (
             f"silenceremove="
             f"stop_periods=-1:"
             f"stop_duration={min_duration}:"
             f"stop_threshold={threshold_db}dB"
         ),
         dst, "-y"])
    ok(f"Pausen entfernt → {dst}")


# ── Schritt 3: Segmente schneiden ───────────────────────────────────────────
def parse_segments(segments_str):
    """
    Parst "0:30-3:45,4:00-8:30" in [(30.0, 225.0), (240.0, 510.0)]
    Unterstützt: mm:ss, hh:mm:ss, und reine Sekunden
    """
    def to_seconds(t):
        parts = t.strip().split(":")
        parts = [float(p) for p in parts]
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        else:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]

    result = []
    for seg in segments_str.split(","):
        start_str, end_str = seg.strip().split("-")
        result.append((to_seconds(start_str), to_seconds(end_str)))
    return result


def cut(src, dst, segments_str):
    """
    Schneidet Segmente aus dem Video und verbindet sie nahtlos.
    segments_str: "0:30-3:45,4:00-8:30" (oder Sekunden: "30-225,240-510")

    Workflow:
      1. Jedes Segment wird mit Re-Encode ausgeschnitten (frame-genaue Cuts)
      2. Alle Segmente werden mit concat demuxer verbunden
    """
    segments = parse_segments(segments_str)
    info(f"Schneide {len(segments)} Segment(e) aus {src}")

    tmpdir = tempfile.mkdtemp(prefix="finndigital_cut_")
    try:
        tmp_files = []
        for i, (start, end) in enumerate(segments):
            tmp = os.path.join(tmpdir, f"seg_{i:03d}.mp4")
            duration = end - start
            run(["ffmpeg",
                 "-ss", f"{start:.3f}",
                 "-i", str(src),
                 "-t", f"{duration:.3f}",
                 "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                 "-c:a", "aac", "-b:a", "192k",
                 "-avoid_negative_ts", "make_zero",
                 tmp, "-y"], quiet=True)
            tmp_files.append(tmp)
            ok(f"  Segment {i+1}: {start:.1f}s – {end:.1f}s")

        # Concat-Liste schreiben
        list_path = os.path.join(tmpdir, "list.txt")
        with open(list_path, "w") as f:
            for tf in tmp_files:
                f.write(f"file '{tf}'\n")

        run(["ffmpeg",
             "-f", "concat", "-safe", "0",
             "-i", list_path,
             "-c", "copy",
             dst, "-y"])
        ok(f"Segmente verbunden → {dst}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Schritt 4: Finaler Export ───────────────────────────────────────────────
def finalize(src, dst, fade_duration=0.5):
    """
    Rendert das finale Video:
    - 1920×1080, H.264 High Profile
    - Fade-In (0.5s) + Fade-Out (0.5s)
    - AAC 192kbps
    - faststart (Web-Streaming)
    - yuv420p (maximale Kompatibilität)
    """
    info(f"Finaler Export: {src}")
    duration = get_duration(src)
    fade_out_start = duration - fade_duration

    run(["ffmpeg", "-i", str(src),
         "-vf", (
             f"scale=1920:1080:force_original_aspect_ratio=decrease,"
             f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,"
             f"fade=t=in:st=0:d={fade_duration},"
             f"fade=t=out:st={fade_out_start:.3f}:d={fade_duration}"
         ),
         "-af", (
             f"afade=t=in:st=0:d={fade_duration},"
             f"afade=t=out:st={fade_out_start:.3f}:d={fade_duration}"
         ),
         "-c:v", "libx264", "-crf", "20", "-preset", "slow",
         "-profile:v", "high", "-level", "4.1",
         "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart",
         "-pix_fmt", "yuv420p",
         dst, "-y"])
    ok(f"Finales Video → {dst}")


# ── Auto-Modus: alles in einem Schritt ─────────────────────────────────────
def auto(src, dst):
    """
    Vollautomatische Verarbeitung:
      Rohdatei → Normalisieren → Stille raus → Finaler Export
    (Segmentschnitt muss separat mit 'cut' gemacht werden)
    """
    tmpdir = tempfile.mkdtemp(prefix="finndigital_auto_")
    try:
        step1 = os.path.join(tmpdir, "1_normalized.mp4")
        step2 = os.path.join(tmpdir, "2_no_silence.mp4")

        print(f"\n{B}━━━ finndigital Auto-Prozess ━━━{X}")
        print(f"Eingabe:  {src}")
        print(f"Ausgabe:  {dst}\n")

        normalize(src, step1)
        remove_silence(step1, step2)
        finalize(step2, dst)

        duration = get_duration(dst)
        print(f"\n{G}━━━ Fertig! ━━━{X}")
        print(f"Länge: {duration/60:.1f} Minuten")
        print(f"Datei: {dst}\n")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    require_ffmpeg()

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "normalize" and len(sys.argv) == 4:
        normalize(sys.argv[2], sys.argv[3])

    elif cmd == "silence" and len(sys.argv) == 4:
        remove_silence(sys.argv[2], sys.argv[3])

    elif cmd == "cut" and len(sys.argv) == 5:
        cut(sys.argv[2], sys.argv[3], sys.argv[4])

    elif cmd == "finalize" and len(sys.argv) == 4:
        finalize(sys.argv[2], sys.argv[3])

    elif cmd == "auto" and len(sys.argv) == 4:
        auto(sys.argv[2], sys.argv[3])

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
