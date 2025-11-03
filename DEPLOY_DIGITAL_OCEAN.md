# Deploy to Digital Ocean - Step by Step

Simple deployment guide for NeuTTS Air API on Digital Ocean droplet.

## Prerequisites

- Digital Ocean account
- Droplet with Docker installed (or follow setup below)

---

## Step 1: Create Digital Ocean Droplet

1. **Go to** Digital Ocean Dashboard
2. **Create Droplet:**
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic (4GB RAM minimum recommended)
   - **CPU:** 2 vCPUs or more
   - **Region:** Choose closest to users
   - **Authentication:** SSH key (recommended)

3. **Note your droplet IP:** `123.456.789.0`

---

## Step 2: Connect to Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

---

## Step 3: Install Docker (if not installed)

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

---

## Step 4: Upload Project Files

### Option A: Using Git (Recommended)

```bash
# On your droplet
cd ~
git clone https://github.com/your-repo/neutts-air.git
cd neutts-air
```

### Option B: Using SCP

```bash
# From your local machine
scp -r /path/to/neutts-air root@YOUR_DROPLET_IP:~/
```

---

## Step 5: Configure Environment

```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Change this line:
# - BASE_URL=http://YOUR_DROPLET_IP:8001
# To your actual IP:
# - BASE_URL=http://123.456.789.0:8001
```

**Example:**
```yaml
environment:
  - BASE_URL=http://123.456.789.0:8001
```

Save and exit (Ctrl+X, Y, Enter)

---

## Step 6: Build and Run

```bash
# Build Docker image
docker-compose build

# Start the service
docker-compose up -d

# Check if running
docker-compose ps
```

**Expected output:**
```
NAME              STATUS    PORTS
neutts-air-api    Up        0.0.0.0:8001->8001/tcp
```

---

## Step 7: Verify Deployment

```bash
# Check logs
docker-compose logs -f

# Test health endpoint
curl http://localhost:8001/
```

**Should return:**
```json
{
  "status": "ok",
  "model": "NeuTTS Air Q8 GGUF",
  "available_voices": ["dave", "jo"],
  "default_voice": "dave"
}
```

---

## Step 8: Test from Your Machine

```bash
# Replace with your droplet IP
curl http://123.456.789.0:8001/

# Test synthesis
curl -X POST http://123.456.789.0:8001/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Digital Ocean", "voice": "dave"}'
```

**Response will contain FULL URL:**
```json
{
  "audio_url": "http://123.456.789.0:8001/audio/uuid.wav",
  "duration": 2.5,
  "voice": "dave",
  "generation_time": 1.8
}
```

---

## Step 9: Configure Firewall

```bash
# Allow port 8001
ufw allow 8001/tcp
ufw status
```

---

## Mobile App Usage

Your mobile app can now directly use the audio URL:

```javascript
// Example: React Native
const response = await fetch('http://123.456.789.0:8001/synthesize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'Hello', voice: 'dave'})
});

const data = await response.json();

// Play audio directly from URL
const audioUrl = data.audio_url; // Full URL: http://123.456.789.0:8001/audio/uuid.wav
const sound = new Sound(audioUrl, '', (error) => {
  if (!error) sound.play();
});
```

---

## Management Commands

### View Logs
```bash
docker-compose logs -f
```

### Restart Service
```bash
docker-compose restart
```

### Stop Service
```bash
docker-compose down
```

### Update Code
```bash
git pull
docker-compose build
docker-compose up -d
```

### Check Resource Usage
```bash
docker stats neutts-air-api
```

---

## Persistence

**Data that persists across restarts:**
- ✅ Voice references in `samples/`
- ✅ Generated audio in `output/`

**Volumes mounted:**
```
./samples -> /app/samples  (voice references)
./output -> /app/output   (generated audio)
```

---

## Adding New Voices

```bash
# From local machine
curl -X POST http://123.456.789.0:8001/voices/add \
  -F "voice_name=alice" \
  -F "audio_file=@alice.wav" \
  -F "reference_text=Hello, this is Alice speaking"
```

Files are automatically saved to `samples/` directory (persistent).

---

## Troubleshooting

### Container won't start
```bash
docker-compose logs
```

### Out of memory
Increase droplet size or switch to Q4 model:
- Edit `api/server.py` line 46
- Change `q8` to `q4`
- Rebuild: `docker-compose build && docker-compose up -d`

### Can't access from outside
```bash
# Check firewall
ufw status

# Allow port
ufw allow 8001/tcp

# Check if service is running
curl http://localhost:8001/
```

### Audio quality issues
- Use Q8 model (current default - better quality)
- For faster generation, use Q4 model

---

## Cost Estimate

**Digital Ocean Droplet:**
- **4GB RAM, 2 vCPUs:** ~$24/month
- **8GB RAM, 4 vCPUs:** ~$48/month (recommended for production)

---

## Security Notes

As requested:
- ❌ No SSL/HTTPS
- ❌ No domain
- ❌ No authentication
- ✅ Direct IP access

**For production with users, consider:**
- Adding API key authentication
- Using HTTPS (Let's Encrypt)
- Rate limiting
- Domain name

---

## Quick Reference

**Your API Base URL:**
```
http://YOUR_DROPLET_IP:8001
```

**Main endpoint:**
```bash
POST http://YOUR_DROPLET_IP:8001/synthesize
{
  "text": "Hello world",
  "voice": "dave"
}
```

**Response format:**
```json
{
  "audio_url": "http://YOUR_DROPLET_IP:8001/audio/uuid.wav",
  "duration": 3.5,
  "voice": "dave",
  "generation_time": 2.1
}
```

Mobile app gets full URL and can play immediately! 🚀
