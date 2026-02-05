# 🚀 DEPLOYMENT CHECKLIST

## ✅ Pre-Deployment Verification

### 1. Required Files Present
- [ ] `api.py` (root directory)
- [ ] `requirements.txt`
- [ ] `src/__init__.py`
- [ ] `src/feature_engineering.py`
- [ ] `src/anomaly_detection.py`
- [ ] `src/decision_engine.py`
- [ ] `reports/human_feature_profile.json`
- [ ] `reports/human_anomaly_thresholds.json`
- [ ] `.gitignore`
- [ ] `DEPLOYMENT_GUIDE.md`

### 2. Local Testing
```bash
# Test locally first
cd e:/HCL
uvicorn api:app --port 8000

# In another terminal, test health
curl http://localhost:8000/health

# Test detection (with sample audio)
curl -X POST "http://localhost:8000/detect" \
  -H "x-api-key: HCL_AI_VOICE_DETECTION_2026" \
  -H "Content-Type: application/json" \
  -d '{"language":"en","audio_format":"mp3","audio_base64_format":"..."}'
```

### 3. GitHub Repository Setup
```bash
# Initialize git
git init
git add .
git commit -m "Deploy: AI Voice Detection API"

# Create GitHub repo and push
git remote add origin <YOUR_GITHUB_REPO_URL>
git branch -M main
git push -u origin main
```

---

## 🌐 Render Deployment Steps

### Step 1: Create Web Service
1. Go to https://render.com
2. Sign in / Sign up
3. Click "New +" → "Web Service"
4. Connect GitHub repository

### Step 2: Configure Service

**Name**: `ai-voice-detection-api`

**Build Command**:
```
pip install -r requirements.txt
```

**Start Command**:
```
uvicorn api:app --host 0.0.0.0 --port $PORT
```

**Environment Variables**:
```
API_KEY=HCL_AI_VOICE_DETECTION_2026
```

**Health Check Path**:
```
/health
```

**Instance Type**: Starter ($7/month recommended)

### Step 3: Deploy
- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Note the public URL: `https://your-app.onrender.com`

---

## ✅ Post-Deployment Verification

### 1. Health Check
```bash
curl https://your-app.onrender.com/health
```
**Expected**: `{"status":"ok"}`

### 2. API Info
```bash
curl https://your-app.onrender.com/info \
  -H "x-api-key: HCL_AI_VOICE_DETECTION_2026"
```

### 3. Detection Test
```bash
curl -X POST "https://your-app.onrender.com/detect" \
  -H "x-api-key: HCL_AI_VOICE_DETECTION_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "audio_format": "mp3",
    "audio_base64_format": "<BASE64_AUDIO>"
  }'
```
**Expected**: `{"classification":"HUMAN","confidence":0.XXX}`

### 4. Official Endpoint Tester
- Open the official Endpoint Tester UI
- Enter your Render URL
- Enter API key: `HCL_AI_VOICE_DETECTION_2026`
- Test with sample audio
- Verify response format

---

## 🎯 Final Checklist

- [ ] API deployed to Render
- [ ] Public HTTPS URL obtained
- [ ] Health endpoint returns 200
- [ ] Detection endpoint works
- [ ] Response format is correct (2 fields only)
- [ ] API key authentication works
- [ ] Latency < 2 seconds
- [ ] Official Endpoint Tester passes
- [ ] Service stable for 24+ hours

---

## 📊 Deployment Summary

| Item | Value |
|------|-------|
| **Platform** | Render |
| **URL** | `https://your-app.onrender.com` |
| **API Key** | `HCL_AI_VOICE_DETECTION_2026` |
| **Header** | `x-api-key` |
| **Endpoint** | `POST /detect` |
| **Health** | `GET /health` |
| **Response** | `{"classification":"...","confidence":...}` |

---

## 🆘 Troubleshooting

### Build Fails
- Check `requirements.txt` is present
- Verify all dependencies are listed
- Check Render build logs

### Server Won't Start
- Verify start command uses `$PORT`
- Check `api.py` is in root directory
- Ensure `src/` directory structure is correct

### 401 Errors
- Verify `API_KEY` environment variable is set
- Check header is `x-api-key` (lowercase)
- Confirm API key value matches

### 500 Errors
- Check Render logs for Python errors
- Verify all required files are in repo
- Ensure `reports/` directory has JSON files

---

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Render Logs**: Dashboard → Your Service → Logs

---

**Status**: Ready for Deployment ✅  
**Estimated Time**: 15-20 minutes total  
**Cost**: $0 (Free) or $7/month (Starter, recommended)
