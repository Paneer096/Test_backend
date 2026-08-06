# Project - Meeting Intelligence

Upload a meeting recording. Ask questions. Get answers with evidence.

## Folder Structure
project/
├── backend/          # Flask server + AI pipeline
│   ├── app.py           # Main server
│   ├── transcriber.py   # Whisper speech-to-text
│   ├── llmprocessor.py  # Groq LLM for extraction + query
│   └── .env.example     # API key template
├── frontend/         # HTML/CSS/JS (to be built)
└── requirements.txt  # Python dependencies

## Backend Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your Groq API key from groq.com
python app.py

## API Endpoints

### Upload Audio
POST /api/upload
- FormData with field "audio" (WAV/MP3 file)
- Returns: { meeting_id, segments, structured_data }

### Ask Question
POST /api/query
- JSON: { meeting_id, question }
- Returns: { answer }

### Get Meeting
GET /api/meeting/<meeting_id>
- Returns full meeting object

### Get Audio File
GET /api/audio/<filename>
- Returns audio file for playback

### Demo Mode
GET /api/demo
- Returns pre-processed demo data instantly

## Structured Data Format
{
  summary: "string",
  decisions: [{ decision, proposed_by, evidence_quote, evidence_timestamp }],
  action_items: [{ task, assigned_to, deadline, evidence_quote, evidence_timestamp }],
  key_points: [{ point, speaker, evidence_quote, evidence_timestamp }],
  knowledge_graph: {
    nodes: [{ id, type }],
    edges: [{ from, to, relation }]
  }
}

## Segments Format
[{ start: 2.5, end: 5.0, text: "hello world" }]
