import whisper
import json
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def ensure_ffmpeg_in_path():
    """Ensure ffmpeg is in PATH, checking WinGet and standard install paths."""
    if not shutil.which("ffmpeg"):
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        possible_dirs = [
            os.path.join(local_app_data, "Microsoft", "WinGet", "Links"),
            "C:\\ProgramData\\chocolatey\\bin",
            "C:\\ffmpeg\\bin",
            "C:\\Program Files\\ffmpeg\\bin",
        ]
        for d in possible_dirs:
            if os.path.exists(os.path.join(d, "ffmpeg.exe")):
                os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
                return
        packages_dir = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages")
        if os.path.exists(packages_dir):
            for root, _, files in os.walk(packages_dir):
                if "ffmpeg.exe" in files:
                    os.environ["PATH"] = root + os.pathsep + os.environ.get("PATH", "")
                    return


def transcribe_audio(audio_path):
    """
    Input: path to audio file
    Output: list of {start, end, text}
    """
    ensure_ffmpeg_in_path()
    print("Loading Whisper model...")
    model = whisper.load_model("tiny")
    
    print(f"Transcribing: {audio_path}")
    result = model.transcribe(
        audio_path,
        word_timestamps=True,
        language=None,
        verbose=False
    )
    
    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": round(seg["start"], 1),
            "end": round(seg["end"], 1),
            "text": seg["text"].strip()
        })
    
    print(f"Done! {len(segments)} segments extracted.")
    return segments


if __name__ == "__main__":
    # Resolve directory paths relative to script location
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(SCRIPT_DIR)
    
    outputs_dir = os.path.join(BASE_DIR, "outputs")
    uploads_dir = os.path.join(BASE_DIR, "uploads")
    os.makedirs(outputs_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Path to audio file (checks uploads/ first, then backend/ folder)
    possible_paths = [
        os.path.join(uploads_dir, "meeting.mp3"),
        os.path.join(SCRIPT_DIR, "meeting.mp3"),
        "meeting.mp3"
    ]
    
    audio_file = None
    for p in possible_paths:
        if os.path.exists(p):
            audio_file = p
            break
            
    if not audio_file:
        print("❌ Error: meeting.mp3 not found!")
        print(f"Please put your audio file in {uploads_dir} or {SCRIPT_DIR}")
        exit(1)
    
    # Transcribe
    segments = transcribe_audio(audio_file)
    
    # Print transcript
    print("\n--- TRANSCRIPT ---")
    for s in segments:
        print(f"[{s['start']}s - {s['end']}s] {s['text']}")
    
    # Save to JSON
    output_path = os.path.join(outputs_dir, "transcript.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)
    
    print(f"\n Transcript saved to {output_path}")