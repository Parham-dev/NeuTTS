# Digital Ocean Deployment Checklist

Quick reference for deploying NeuTTS Air API.

## ✅ What You Have Ready

- [x] Dockerfile
- [x] docker-compose.yml
- [x] API returns full URLs (mobile-ready)
- [x] Auto file cleanup
- [x] Q8 model (better quality)
- [x] Multiple voice support

---

## 📋 Deployment Steps

### 1. Create Droplet
- [ ] Ubuntu 22.04 LTS
- [ ] 4GB+ RAM, 2+ vCPUs
- [ ] Note your IP: `________________`

### 2. Install Docker
```bash
ssh root@YOUR_IP
curl -fsSL https://get.docker.com | sh
apt install docker-compose -y
```

### 3. Upload Code
```bash
# Option A: Git
git clone YOUR_REPO
cd neutts-air

# Option B: SCP from local
scp -r . root@YOUR_IP:~/neutts-air
```

### 4. Configure
```bash
nano docker-compose.yml
# Change: BASE_URL=http://YOUR_DROPLET_IP:8001
```

### 5. Deploy
```bash
docker-compose build
docker-compose up -d
```

### 6. Test
```bash
curl http://localhost:8001/
curl -X POST http://YOUR_IP:8001/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Test", "voice": "dave"}'
```

### 7. Configure Firewall
```bash
ufw allow 8001/tcp
```

---

## 🎯 What Your Mobile App Gets

**Request:**
```json
POST http://YOUR_IP:8001/synthesize
{
  "text": "Hello world",
  "voice": "dave"
}
```

**Response:**
```json
{
  "audio_url": "http://YOUR_IP:8001/audio/abc123.wav",
  "duration": 2.5,
  "voice": "dave",
  "generation_time": 1.8
}
```

**Mobile app:**
- Gets full URL
- Downloads audio
- Plays immediately
- No URL construction needed!

---

## 🔧 Management

**View logs:**
```bash
docker-compose logs -f
```

**Restart:**
```bash
docker-compose restart
```

**Update:**
```bash
git pull
docker-compose build
docker-compose up -d
```

---

## 💰 Cost

- **4GB RAM:** $24/month
- **8GB RAM:** $48/month (recommended)

---

## ⚠️ Before You Deploy

1. [ ] Change `BASE_URL` in docker-compose.yml
2. [ ] Open firewall port 8001
3. [ ] Test locally first with Postman
4. [ ] Ensure samples/ has voice references

---

## 📱 Mobile App Integration

### React Native Example
```javascript
const synthesize = async (text) => {
  const response = await fetch('http://YOUR_IP:8001/synthesize', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text, voice: 'dave'})
  });

  const data = await response.json();
  return data.audio_url; // Full URL ready to play!
};
```

### Flutter Example
```dart
Future<String> synthesize(String text) async {
  final response = await http.post(
    Uri.parse('http://YOUR_IP:8001/synthesize'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'text': text, 'voice': 'dave'}),
  );

  final data = jsonDecode(response.body);
  return data['audio_url']; // Full URL!
}
```

---

## 🚀 Ready to Deploy!

Follow [DEPLOY_DIGITAL_OCEAN.md](DEPLOY_DIGITAL_OCEAN.md) for detailed instructions.
