# NeuTTS Air Streaming API Documentation

## Overview

FastAPI-based REST API for real-time text-to-speech synthesis with voice cloning capabilities using NeuTTS Air.

**Base URL**: `http://localhost:8001`

---

## Features

✅ Real-time streaming TTS synthesis
✅ Multiple voice support
✅ Dynamic voice management (add/delete voices)
✅ Pre-encoded references for minimal latency
✅ GGUF Q4 model + ONNX decoder for speed

---

## Endpoints

### 1. Health Check

**GET** `/`

Returns server status and available voices.

**Response:**
```json
{
  "status": "ok",
  "model": "NeuTTS Air Q4 GGUF",
  "available_voices": ["dave", "jo"],
  "default_voice": "dave",
  "endpoints": { ... }
}
```

---

### 2. List Voices

**GET** `/voices`

List all available voice references.

**Response:**
```json
{
  "voices": [
    {
      "name": "dave",
      "text_path": "samples/dave.txt",
      "codes_path": "samples/dave.pt",
      "audio_path": "samples/dave.wav",
      "has_audio": true
    }
  ],
  "count": 2
}
```

---

### 3. Synthesize (Full Audio)

**POST** `/synthesize`

Generate complete audio file (waits for full generation).

**Request Body:**
```json
{
  "text": "Hello world, this is a test",
  "voice": "dave"  // optional, defaults to "dave"
}
```

**Response Headers:**
- `X-Generation-Time`: Total generation time in seconds
- `X-Audio-Duration`: Audio duration in seconds
- `X-RTF`: Real-time factor (lower is faster)
- `X-Voice`: Voice name used

**Response:** WAV audio file (24kHz, mono, 16-bit PCM)

**Example:**
```bash
curl -X POST http://localhost:8001/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice": "dave"}' \
  --output output.wav
```

---

### 4. Synthesize Stream

**POST** `/synthesize/stream`

Stream audio chunks in real-time as they're generated.

**Request Body:**
```json
{
  "text": "Hello world, this is a streaming test",
  "voice": "jo"
}
```

**Response:** Streaming WAV audio (chunked transfer encoding)

**Example:**
```bash
curl -X POST http://localhost:8001/synthesize/stream \
  -H "Content-Type: application/json" \
  -d '{"text": "Streaming test", "voice": "jo"}' \
  --output stream.wav
```

---

### 5. Add Voice

**POST** `/voices/add`

Upload a new voice reference with audio and transcript.

**Form Data:**
- `voice_name` (string): Alphanumeric name for the voice
- `audio_file` (file): WAV audio file
- `reference_text` (string): Transcript of the audio

**Audio Requirements:**
- Format: WAV
- Channels: Mono
- Sample rate: 16-44 kHz
- Duration: 3-15 seconds
- Quality: Clean, minimal background noise

**Response:**
```json
{
  "status": "success",
  "message": "Voice 'myvoice' added successfully",
  "voice": {
    "name": "myvoice",
    "text_path": "samples/myvoice.txt",
    "codes_path": "samples/myvoice.pt",
    "audio_path": "samples/myvoice.wav"
  }
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8001/voices/add \
  -F "voice_name=alice" \
  -F "audio_file=@alice.wav" \
  -F "reference_text=Hello, my name is Alice and this is my voice"
```

**Example (Python):**
```python
import requests

files = {'audio_file': open('alice.wav', 'rb')}
data = {
    'voice_name': 'alice',
    'reference_text': 'Hello, my name is Alice'
}
response = requests.post(
    'http://localhost:8001/voices/add',
    files=files,
    data=data
)
print(response.json())
```

---

### 6. Delete Voice

**DELETE** `/voices/{voice_name}`

Remove a voice reference from the server.

**Response:**
```json
{
  "status": "success",
  "message": "Voice 'myvoice' deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8001/voices/myvoice
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Text cannot be empty"
}
```

### 404 Not Found
```json
{
  "detail": "Voice 'unknown' not found. Available: ['dave', 'jo']"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Model not initialized"
}
```

---

## Usage Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8001"

# List available voices
voices = requests.get(f"{BASE_URL}/voices").json()
print(f"Available voices: {voices['count']}")

# Synthesize with specific voice
response = requests.post(
    f"{BASE_URL}/synthesize",
    json={
        "text": "Hello, this is a test",
        "voice": "dave"
    }
)

# Save audio
with open("output.wav", "wb") as f:
    f.write(response.content)

# Check performance metrics
print(f"Generation time: {response.headers.get('X-Generation-Time')}s")
print(f"Audio duration: {response.headers.get('X-Audio-Duration')}s")
print(f"RTF: {response.headers.get('X-RTF')}x")
```

### JavaScript/Fetch

```javascript
// Synthesize speech
async function synthesize(text, voice = 'dave') {
  const response = await fetch('http://localhost:8001/synthesize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, voice })
  });

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);

  // Play audio
  const audio = new Audio(url);
  audio.play();
}

synthesize("Hello world!", "jo");
```

---

## Performance

- **Model**: NeuTTS Air Q4 GGUF (quantized)
- **Codec**: ONNX decoder (no encoder overhead)
- **Reference**: Pre-encoded at startup
- **Chunk size**: ~0.5s audio per chunk (12,000 samples @ 24kHz)
- **RTF**: Typically < 1.0x (faster than real-time)

---

## Starting the Server

```bash
# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart

# Start server
python server.py

# Server runs on http://0.0.0.0:8001
```

---

## Testing

Run the included test suite:

```bash
python test_api.py
```

---

## Notes

- Voice names must be alphanumeric
- Default voice is "dave" if not specified
- Audio output is always 24kHz, mono, 16-bit PCM WAV
- Streaming endpoint uses chunked transfer encoding
- All generated audio is watermarked using Perth watermarker
