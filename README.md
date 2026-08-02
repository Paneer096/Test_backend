
#  Project - Meeting Intelligence

Upload a meeting recording. Ask questions. Get answers with proof.

---

## Folder Structure

    project/
    ├── backend/
    │   ├── app.py              # Flask server
    │   ├── transcriber.py      # Whisper speech-to-text
    │   ├── llmprocessor.py     # Groq LLM extraction and query
    │   └── .env.example        # API key template
    ├── frontend/
    │   └── index.html          # Web interface
    ├── uploads/                # Audio files go here
    ├── outputs/                # JSON results appear here
    ├── requirements.txt        # Python dependencies
    └── README.md


---

## Setup

```bash
# Clone the repo
git clone https://github.com/Paneer096/Test_backend.git
cd Test_backend

# Install dependencies
pip install -r requirements.txt

# Set up API key
cp backend/.env.example backend/.env
# Edit backend/.env and add your Groq API key from groq.com

# Run the server
python backend/app.py
Open http://localhost:5000

API Endpoints
Method	Endpoint	Description
POST	/api/upload	Upload audio file (FormData field: "audio")
POST	/api/query	Ask question (JSON: meeting_id, question)
GET	/api/meeting/<id>	Get full meeting data
GET	/api/audio/<filename>	Get audio file for playback
GET	/api/demo	Load pre-processed demo data
How It Works
User uploads meeting audio

Whisper transcribes speech to text with timestamps

Groq LLM extracts decisions, action items, key points, knowledge graph

User asks questions in natural language

LLM answers with timestamped evidence

Click any timestamp to jump to that moment in audio

Tech Stack
Python + Flask (backend)

OpenAI Whisper (speech-to-text)

Groq API + Llama 3.1 (LLM)

HTML/CSS/JavaScript (frontend)

Notes
Copy backend/.env.example to backend/.env and add your Groq API key

Place audio files in the uploads/ folder

Processed JSON files appear in outputs/
