import whisper
import json
import os

def transcribe_audio(audio_path):
    """
    Input: path to audio file
    Output: list of {start, end, text}
    """
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
    # Create outputs folder if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # Path to your audio file
    audio_file = "uploads/meeting.mp3"  # Make sure this file exists
    
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"❌ Error: {audio_file} not found!")
        print("Please put your audio file in backend/uploads/demo.wav")
        exit(1)
    
    # Transcribe
    segments = transcribe_audio(audio_file)
    
    # Print transcript
    print("\n--- TRANSCRIPT ---")
    for s in segments:
        print(f"[{s['start']}s - {s['end']}s] {s['text']}")
    
    # Save to JSON
    output_path = "outputs/transcript.json"
    with open(output_path, "w") as f:
        json.dump(segments, f, indent=2)
    
    print(f"\n✅ Transcript saved to {output_path}")