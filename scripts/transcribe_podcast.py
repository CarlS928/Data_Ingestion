"""
Podcast Transcriber

Transcribes an MP3 file to text using faster-whisper (a local, CPU-friendly
reimplementation of OpenAI's Whisper model - no API key or internet access
needed once the model has been downloaded once).

Run with:
    python scripts/transcribe_podcast.py [path/to/audio.mp3]
    (defaults to the Morning Call episode in the repo root if no path is given)

Output:
    outputs/<audio filename>_transcript.txt   - plain-paragraph transcript
    outputs/<audio filename>_transcript.srt   - timestamped subtitle-style transcript

Model size / speed trade-off (all run on CPU here):
    tiny   - fastest, roughest
    base   - good default for spoken-word podcasts (used below)
    small  - noticeably more accurate, ~2-3x slower than base
    medium/large - best accuracy, considerably slower on CPU
Change MODEL_SIZE below to trade accuracy for speed.
"""

import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel

MODEL_SIZE = "base"
DEFAULT_AUDIO = Path(__file__).resolve().parent.parent / "Morning_Call_2026-09-23_AI_oil_and_rates_drive_the_market_outlook.mp3"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def format_timestamp(seconds):
    """SRT timestamp format: HH:MM:SS,mmm"""
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def transcribe(audio_path):
    print(f"Loading the '{MODEL_SIZE}' Whisper model (downloads once, then reused)...")
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

    print(f"Transcribing {audio_path.name} - this can take a while for a long episode...")
    start = time.time()
    segments, info = model.transcribe(str(audio_path), beam_size=5)

    print(f"Detected language: {info.language} (confidence {info.language_probability:.0%})")
    print(f"Audio duration: {info.duration / 60:.1f} minutes\n")

    collected = []
    for segment in segments:
        collected.append(segment)
        stamp = format_timestamp(segment.start)[:8]
        print(f"[{stamp}] {segment.text.strip()}")

    elapsed = time.time() - start
    print(f"\nTranscription finished in {elapsed / 60:.1f} minutes.")
    return collected, info


def write_outputs(segments, audio_path):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = audio_path.stem

    txt_path = OUTPUT_DIR / f"{stem}_transcript.txt"
    txt_path.write_text(" ".join(s.text.strip() for s in segments), encoding="utf-8")

    srt_path = OUTPUT_DIR / f"{stem}_transcript.srt"
    with srt_path.open("w", encoding="utf-8") as f:
        for i, s in enumerate(segments, start=1):
            f.write(f"{i}\n{format_timestamp(s.start)} --> {format_timestamp(s.end)}\n{s.text.strip()}\n\n")

    return txt_path, srt_path


def main():
    audio_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_AUDIO
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    segments, info = transcribe(audio_path)
    txt_path, srt_path = write_outputs(segments, audio_path)

    print(f"\nSaved plain transcript to {txt_path}")
    print(f"Saved timestamped transcript to {srt_path}")


if __name__ == "__main__":
    main()
