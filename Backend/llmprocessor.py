from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_meeting_data(segments):
    """
    Input: transcript segments from Whisper
    Output: structured JSON with decisions, action items, knowledge graph
    """
    
    # Convert segments to formatted text
    transcript_text = ""
    for seg in segments:
        timestamp = f"[{seg['start']}s]"
        transcript_text += f"{timestamp} {seg['text']}\n"
    
    prompt = """Analyze this meeting transcript. Extract the following in JSON format:

1. summary: One paragraph summary of the meeting (2-3 sentences)

2. decisions: Array of decisions made. Each with:
   - decision: What was decided
   - proposed_by: Who suggested it
   - evidence_quote: Exact words spoken
   - evidence_timestamp: Timestamp from transcript

3. action_items: Array of tasks assigned. Each with:
   - task: What to do
   - assigned_to: Who will do it
   - deadline: When (if mentioned)
   - evidence_quote: Exact words
   - evidence_timestamp: Timestamp

4. key_points: Array of important statements. Each with:
   - point: What was said
   - speaker: Who said it
   - evidence_quote: Exact words
   - evidence_timestamp: Timestamp

5. knowledge_graph:
   - nodes: Array of {id, type} where type is "person", "decision", "topic", "money"
   - edges: Array of {from, to, relation} where relation is "proposed", "opposed", "supported", "assigned_to"

IMPORTANT: Output ONLY valid JSON. No markdown. No explanations. Every item MUST have evidence_quote and evidence_timestamp."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You extract structured data from meeting transcripts. Output only valid JSON."},
            {"role": "user", "content": f"{prompt}\n\nTRANSCRIPT:\n{transcript_text}"}
        ],
        temperature=0.1,
        max_tokens=4096
    )
    
    raw = response.choices[0].message.content
    
    # Clean up JSON
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
    
    try:
        data = json.loads(raw)
        return data
    except:
        return {"error": "JSON parse failed", "raw": raw}


def query_meeting(segments, structured_data, user_question):
    """
    Answer user question with evidence
    """
    
    transcript_text = ""
    for seg in segments:
        transcript_text += f"[{seg['start']}s] {seg['text']}\n"
    
    structured_text = json.dumps(structured_data, indent=2)
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": f"""You answer questions about a meeting.
            
Rules:
- Answer in the same language as the question (Hindi → Hindi, English → English)
- Always include evidence: quote the exact words AND give the timestamp
- Format evidence like: [timestamp] "exact quote"
- Keep answers under 4 sentences
- If the answer isn't in the meeting, say so honestly

Here is the structured meeting data:
{structured_text}"""},
            {"role": "user", "content": f"TRANSCRIPT:\n{transcript_text}\n\nQUESTION: {user_question}"}
        ],
        temperature=0.1,
        max_tokens=500
    )
    
    return response.choices[0].message.content


# Test
if __name__ == "__main__":
    import os
    
    # Create outputs folder if needed (outside backend)
    os.makedirs("../outputs", exist_ok=True)
    
    # Check if transcript exists from transcriber
    if os.path.exists("../outputs/transcript.json"):
        print("Loading existing transcript...")
        with open("../outputs/transcript.json", "r") as f:
            segments = json.load(f)
    else:
        # If no transcript, run transcriber
        from transcriber import transcribe_audio
        
        audio_file = "../uploads/meeting.mp3"
        if not os.path.exists(audio_file):
            print(f"❌ Error: {audio_file} not found!")
            print("Put your audio file in the uploads/ folder")
            exit(1)
        
        print("Transcribing audio...")
        segments = transcribe_audio(audio_file)
        
        # Save transcript
        with open("../outputs/transcript.json", "w") as f:
            json.dump(segments, f, indent=2)
        print("Saved: ../outputs/transcript.json")
    
    # Extract structured data
    print("Extracting meeting data...")
    data = extract_meeting_data(segments)
    
    # Save structured data
    with open("../outputs/structured_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Saved: ../outputs/structured_data.json")
    
    # Show result
    print("\n--- EXTRACTED DATA ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # Test queries
    if "error" not in data:
        print("\n--- TESTING QUERIES ---")
        questions = [
            "What was decided in this meeting?",
            "Who has action items?",
            "Summarize this meeting in one sentence."
        ]
        for q in questions:
            print(f"\n❓ {q}")
            answer = query_meeting(segments, data, q)
            print(f"💬 {answer}")
    else:
        print("\n⚠️ Extraction failed. Check raw output above.")