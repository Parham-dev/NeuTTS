# Postman API Testing Examples

Test your NeuTTS Air API with these Postman requests.

## Base URL
```
http://localhost:8001
```

---

## 1. Health Check

**Method:** `GET`
**URL:** `http://localhost:8001/`

**Response:**
```json
{
  "status": "ok",
  "model": "NeuTTS Air Q8 GGUF",
  "available_voices": [
    "dave",
    "jo"
  ],
  "default_voice": "dave"
}
```

---

## 2. List Available Voices

**Method:** `GET`
**URL:** `http://localhost:8001/voices`

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
    },
    {
      "name": "jo",
      "text_path": "samples/jo.txt",
      "codes_path": "samples/jo.pt",
      "audio_path": "samples/jo.wav",
      "has_audio": true
    }
  ],
  "count": 2
}
```

---

## 3. Synthesize Speech (Main Endpoint)

**Method:** `POST`
**URL:** `http://localhost:8001/synthesize`

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "text": "Hello, my name is Dave. How can I help you today?",
  "voice": "dave"
}
```

**Response:**
```json
{
  "audio_url": "/audio/85d5d0c4-5e49-4de3-a16b-57370e3058de.wav",
  "duration": 3.52,
  "voice": "dave",
  "generation_time": 2.13
}
```

**To download the audio:**
- Copy the `audio_url` from response
- Make a new GET request: `http://localhost:8001/audio/85d5d0c4-5e49-4de3-a16b-57370e3058de.wav`
- Click "Send and Download" in Postman

---

## 4. Synthesize with Different Voice

**Method:** `POST`
**URL:** `http://localhost:8001/synthesize`

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "text": "Hi there, I'm Jo. Nice to meet you!",
  "voice": "jo"
}
```

**Response:**
```json
{
  "audio_url": "/audio/a1b2c3d4-5678-90ab-cdef-1234567890ab.wav",
  "duration": 2.5,
  "voice": "jo",
  "generation_time": 1.8
}
```

---

## 5. Test with Long Text

**Method:** `POST`
**URL:** `http://localhost:8001/synthesize`

**Body (raw JSON):**
```json
{
  "text": "Artificial intelligence is transforming the way we interact with technology. Voice synthesis has reached a point where it can produce natural-sounding speech that is almost indistinguishable from human voices. This opens up incredible possibilities for accessibility, entertainment, and communication.",
  "voice": "dave"
}
```

---

## 6. Streaming Endpoint (Real-time)

**Method:** `POST`
**URL:** `http://localhost:8001/synthesize/stream`

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "text": "This is streaming audio generation in real-time",
  "voice": "dave"
}
```

**Response:**
- Returns WAV audio file directly (streaming chunks)
- Use "Send and Download" in Postman

---

## 7. Add New Voice

**Method:** `POST`
**URL:** `http://localhost:8001/voices/add`

**Headers:**
- None needed (multipart/form-data auto-detected)

**Body (form-data):**

| Key | Value | Type |
|-----|-------|------|
| `voice_name` | `alice` | Text |
| `audio_file` | Select `.wav` file | File |
| `reference_text` | `Hello, my name is Alice and this is my voice` | Text |

**Response:**
```json
{
  "status": "success",
  "message": "Voice 'alice' added successfully"
}
```

---

## 8. Delete Voice

**Method:** `DELETE`
**URL:** `http://localhost:8001/voices/alice`

**Response:**
```json
{
  "status": "success",
  "message": "Voice 'alice' deleted successfully"
}
```

---

## 9. Download Generated Audio

**Method:** `GET`
**URL:** `http://localhost:8001/audio/85d5d0c4-5e49-4de3-a16b-57370e3058de.wav`

**Note:** Replace the UUID with the actual `audio_url` from synthesis response.

**Response:**
- WAV audio file download
- Use "Send and Download" button in Postman

---

## Error Examples

### Missing Text
**Request:**
```json
{
  "text": "",
  "voice": "dave"
}
```

**Response (400):**
```json
{
  "detail": "Text cannot be empty"
}
```

### Invalid Voice
**Request:**
```json
{
  "text": "Hello",
  "voice": "unknown"
}
```

**Response (404):**
```json
{
  "detail": "Voice 'unknown' not found. Available: ['dave', 'jo']"
}
```

---

## Quick Test Workflow in Postman

1. **Import Collection:**
   - Create new collection: "NeuTTS Air API"
   - Add requests from above

2. **Test Flow:**
   ```
   GET /              → Check server is running
   GET /voices        → See available voices
   POST /synthesize   → Generate audio (get URL)
   GET /audio/{uuid}  → Download audio file
   ```

3. **Set Environment Variable:**
   - Variable: `base_url`
   - Value: `http://localhost:8001`
   - Use: `{{base_url}}/synthesize`

---

## Expected Response Structure

### Synthesis Success:
```json
{
  "audio_url": "/audio/<uuid>.wav",     // URL to download audio
  "duration": 3.52,                      // Audio length in seconds
  "voice": "dave",                       // Voice used
  "generation_time": 2.13                // How long it took to generate
}
```

### What you get:
1. **JSON response** with audio URL
2. **Download** audio from the URL
3. **Play** the WAV file

---

## Tips for Postman

- ✅ Use **Collections** to organize requests
- ✅ Set **Environment Variables** for base URL
- ✅ Use **Tests** tab to auto-extract audio_url:
  ```javascript
  pm.environment.set("audio_url", pm.response.json().audio_url);
  ```
- ✅ Chain requests: Synthesize → Download using `{{audio_url}}`
- ✅ Save responses to see JSON structure
- ✅ Use "Send and Download" for audio files
