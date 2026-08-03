from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from transcriber import transcribe_audio
from llmprocessor import extract_meeting_data, query_meeting

app = Flask(__name__)
CORS(app)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

meetings = {}


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)


@app.route("/api/upload", methods=["POST"])
def upload():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400
    
    file = request.files["audio"]
    
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"{meeting_id}.wav"
    audio_path = os.path.join(UPLOADS_DIR, audio_filename)
    file.save(audio_path)
    
    print(f"📁 Saved audio: {audio_path}")
    
    try:
        print("🎤 Transcribing...")
        segments = transcribe_audio(audio_path)
        print(f"✅ Transcription done: {len(segments)} segments")
        
        print("🧠 Extracting meeting data...")
        structured_data = extract_meeting_data(segments)
        print("✅ Extraction done")
        
        meetings[meeting_id] = {
            "meeting_id": meeting_id,
            "segments": segments,
            "structured_data": structured_data,
            "audio_filename": audio_filename
        }
        
        with open(os.path.join(OUTPUTS_DIR, f"{meeting_id}.json"), "w", encoding="utf-8") as f:
            json.dump(meetings[meeting_id], f, indent=2, ensure_ascii=False)
        
        return jsonify({
            "meeting_id": meeting_id,
            "segments": segments,
            "structured_data": structured_data
        })
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/query", methods=["POST"])
def query():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data sent"}), 400
    
    meeting_id = data.get("meeting_id")
    question = data.get("question")
    
    if not meeting_id:
        return jsonify({"error": "Missing meeting_id"}), 400
    
    if not question:
        return jsonify({"error": "Missing question"}), 400
    
    if meeting_id not in meetings:
        return jsonify({"error": "Meeting not found"}), 404
    
    meeting = meetings[meeting_id]
    
    try:
        print(f"❓ Query: {question}")
        answer = query_meeting(meeting["segments"], meeting["structured_data"], question)
        print(f"💬 Answer: {answer[:100]}...")
        
        return jsonify({"question": question, "answer": answer})
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/meeting/<meeting_id>", methods=["GET"])
def get_meeting(meeting_id):
    if meeting_id not in meetings:
        return jsonify({"error": "Meeting not found"}), 404
    return jsonify(meetings[meeting_id])


@app.route("/api/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(UPLOADS_DIR, filename)


@app.route("/api/demo", methods=["GET"])
def demo():
    demo_file = os.path.join(OUTPUTS_DIR, "demo_data.json")
    if os.path.exists(demo_file):
        with open(demo_file, "r", encoding="utf-8") as f:
            demo_data = json.load(f)
        meeting_id = demo_data["meeting_id"]
        meetings[meeting_id] = demo_data
        return jsonify(demo_data)
    else:
        return jsonify({"error": "Demo data not found"}), 404


if __name__ == "__main__":
    print("=" * 50)
    print("🎙️  VAANI Server Starting...")
    print("Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)