# NeuTTS Air API

Clean, production-ready API for real-time text-to-speech with voice cloning.

## 🎯 What Changed (Refactored)

### ✅ Completed Tasks
1. **API now returns URLs** instead of raw audio files
2. **Auto-cleanup** of old generated files (keeps last 100)
3. **Clean project structure** - organized code layout
4. **Mobile-ready** - JSON responses with audio URLs

### 📁 New Structure

```
neutts-air/
├── api/                    # API server code
│   ├── server.py          # Main FastAPI app
│   ├── models.py          # Request/response models
│   └── voice_manager.py   # Voice loading logic
├── output/                 # Generated audio files (auto-cleanup)
├── tests/                  # Test scripts
│   └── test_api.py
├── docs/
│   └── API.md             # Full API documentation
├── samples/                # Voice references
├── neuttsair/             # Core TTS library
├── examples/              # Original examples
└── run_server.py          # Server entry point
```

## 🚀 Quick Start

### Start Server
```bash
python run_server.py
```

Server runs on: `http://localhost:8001`
API Docs: `http://localhost:8001/docs`

### Test API
```bash
python tests/test_api.py
```

## 📡 API Response Format

### Before (Old)
```bash
curl POST /synthesize
# Returns: Raw WAV file (not mobile-friendly)
```

### After (New) ✅
```bash
curl POST /synthesize
# Returns:
{
  "audio_url": "/audio/uuid.wav",
  "duration": 3.5,
  "voice": "dave",
  "generation_time": 1.8
}
```

**Mobile App Usage:**
1. POST to `/synthesize` with text + voice
2. Get JSON response with `audio_url`
3. Download audio from URL
4. Play to user

## 🔧 Key Features

✅ **URL-based responses** - Perfect for mobile apps
✅ **Auto-cleanup** - Removes old files automatically (keeps 100)
✅ **Multiple voices** - Dave, Jo, or add your own
✅ **Streaming support** - Real-time audio generation
✅ **Production-ready** - Clean code, modular design

## 📊 Performance

- **Generation**: Faster than real-time (RTF < 1.0)
- **First chunk**: ~1-2 seconds
- **Model**: GGUF Q4 (quantized, fast)
- **Codec**: ONNX decoder (no encoder overhead)

## 🐳 Ready for Docker

The refactored structure is ready for containerization:

**What you need to mount:**
- `samples/` - Voice references (persistent)
- `output/` - Generated audio files (can be ephemeral)

**Next Steps:**
1. Create Dockerfile (simple Python image)
2. Mount volumes for samples/ and output/
3. Deploy to Digital Ocean
4. Access via droplet IP:8001

## 📝 Example Usage

### Python
```python
import requests

# Synthesize speech
response = requests.post(
    "http://localhost:8001/synthesize",
    json={"text": "Hello world", "voice": "dave"}
)

data = response.json()
print(f"Audio URL: {data['audio_url']}")
print(f"Duration: {data['duration']}s")

# Download audio
audio_url = f"http://localhost:8001{data['audio_url']}"
audio = requests.get(audio_url).content
```

### cURL
```bash
# Synthesize
curl -X POST http://localhost:8001/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "voice": "dave"}'

# Response: {"audio_url": "/audio/uuid.wav", "duration": 2.5, ...}

# Download audio
curl http://localhost:8001/audio/uuid.wav -o output.wav
```

### Mobile App (React Native example)
```javascript
// Synthesize
const response = await fetch('http://server:8001/synthesize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'Hello', voice: 'dave'})
});

const data = await response.json();

// Play audio
const audioUrl = `http://server:8001${data.audio_url}`;
const sound = new Sound(audioUrl, '', (error) => {
  if (!error) sound.play();
});
```

## 🗑️ File Cleanup

Generated audio files are automatically cleaned up:
- Keeps last **100 files**
- Removes oldest files first
- Runs on every synthesis request
- Prevents disk space issues

Adjust in `api/server.py`:
```python
cleanup_old_files(max_files=100)  # Change to your preference
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/voices` | GET | List voices |
| `/synthesize` | POST | Generate audio (returns URL) |
| `/synthesize/stream` | POST | Stream audio chunks |
| `/voices/add` | POST | Upload new voice |
| `/voices/{name}` | DELETE | Remove voice |
| `/audio/{file}` | GET | Download audio file |

## 🎙️ Your Pipeline (Goal)

```
1. LLM generates text
   ↓
2. POST /synthesize {text, voice}
   ↓
3. Get {audio_url}
   ↓
4. Download & play audio
   ↓
5. User speaks (STT - to be added)
   ↓
6. Turn detection (to be added)
   ↓
7. Back to LLM
```

**Current Status:** Steps 1-4 are ready! ✅

## 📦 What's Next

For deployment:
1. Create Dockerfile
2. Test locally with Docker
3. Push to Digital Ocean
4. Mount volumes for persistence
5. Access via IP:8001

No auth, no SSL, no domain needed (as requested).
