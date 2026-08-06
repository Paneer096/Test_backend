import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transcriber import transcribe_audio
from llmprocessor import extract_meeting_data, query_meeting

app = Flask(__name__)
CORS(app)

# Absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
UPLOAD_FOLDER = os.path.join(PROJECT_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(PROJECT_DIR, 'outputs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# In-memory storage
meetings = {}


@app.route("/")
def index():
    return send_from_directory(os.path.join(PROJECT_DIR, 'frontend'), 'index.html')


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(os.path.join(PROJECT_DIR, 'frontend'), path)


@app.route("/api/upload", methods=["POST"])
def upload():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files["audio"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Generate unique meeting ID and preserve original file extension
    meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_ext = os.path.splitext(file.filename)[1].lower()
    audio_filename = f"{meeting_id}{original_ext}"
    audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
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

        # Save to disk
        with open(os.path.join(OUTPUT_FOLDER, f"{meeting_id}.json"), "w") as f:
            json.dump(meetings[meeting_id], f, indent=2, ensure_ascii=False)

        return jsonify({
            "meeting_id": meeting_id,
            "segments": segments,
            "structured_data": structured_data,
            "audio_filename": audio_filename
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

    meeting = meetings.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    try:
        print(f"❓ Query: {question}")
        answer = query_meeting(meeting["segments"], meeting["structured_data"], question)
        return jsonify({"question": question, "answer": answer})
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/meeting/<meeting_id>", methods=["GET"])
def get_meeting(meeting_id):
    meeting = meetings.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    return jsonify(meeting)


@app.route("/api/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/api/demo", methods=["GET"])
def demo():
    demo_path = os.path.join(OUTPUT_FOLDER, "demo_data.json")
    if os.path.exists(demo_path):
        with open(demo_path, "r") as f:
            demo_data = json.load(f)
        meeting_id = demo_data["meeting_id"]
        meetings[meeting_id] = demo_data
        return jsonify(demo_data)
    else:
        return jsonify({"error": "Demo data not found"}), 404


if __name__ == "__main__":
    print("=" * 50)
    print("🎙️  VAANI Server Starting...")
    print(f"Uploads folder: {UPLOAD_FOLDER}")
    print(f"Outputs folder: {OUTPUT_FOLDER}")
    print("Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)