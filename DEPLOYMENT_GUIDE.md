# AI Voice Detection API - Deployment Guide

## 🚀 Deployment on Render

### Prerequisites
- GitHub account
- Render account (free tier available)
- This repository pushed to GitHub

---

## 📋 Step-by-Step Deployment

### 1. Push Code to GitHub

```bash
cd e:/HCL
git init
git add .
git commit -m "Initial commit - AI Voice Detection API"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

### 2. Create Render Web Service

1. Go to [https://render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings**:
- **Name**: `ai-voice-detection-api`
- **Region**: Choose closest to evaluators
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`

**Build & Deploy**:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

**Instance Type**:
- **Free** (for testing) or **Starter** ($7/month, recommended for hackathon)

### 3. Set Environment Variables

In Render Dashboard → Environment:

```
API_KEY=HCL_AI_VOICE_DETECTION_2026
```

### 4. Configure Health Check

In Render Dashboard → Settings → Health Check:

- **Health Check Path**: `/health`
- **Expected Status**: `200`

### 5. Deploy

Click "Create Web Service" - Render will:
1. Clone your repository
2. Install dependencies
3. Start the server
4. Provide a public HTTPS URL

---

## ✅ Verify Deployment

### Test Health Endpoint

```bash
curl https://your-app.onrender.com/health
```

**Expected Response**:
```json
{"status": "ok"}
```

### Test Detection Endpoint

```bash
curl -X POST "https://your-app.onrender.com/detect" \
  -H "x-api-key: HCL_AI_VOICE_DETECTION_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "audio_format": "mp3",
    "audio_base64_format": "UklGRiQAAABXQVZFZm10..."
  }'
```

**Expected Response**:
```json
{
  "classification": "HUMAN",
  "confidence": 0.457
}
```

---

## 📊 Deployment Checklist

### Pre-Deployment
- ✅ Code pushed to GitHub
- ✅ `requirements.txt` present
- ✅ `api.py` in root directory
- ✅ `src/` and `reports/` directories included

### Render Configuration
- ✅ Build command set
- ✅ Start command set
- ✅ Environment variable `API_KEY` configured
- ✅ Health check path `/health` configured
- ✅ Instance type selected

### Post-Deployment
- ✅ Health endpoint returns `{"status": "ok"}`
- ✅ Detection endpoint accepts official format
- ✅ Response contains only `classification` and `confidence`
- ✅ API key authentication works
- ✅ Cold start < 5 seconds
- ✅ Inference < 2 seconds

---

## 🔧 Troubleshooting

### Build Fails

**Issue**: Dependencies not installing

**Solution**: Check `requirements.txt` has all dependencies:
```
fastapi==0.115.6
uvicorn==0.34.0
librosa==0.10.2.post1
soundfile==0.12.1
numpy==1.26.4
scipy==1.14.1
scikit-learn==1.6.1
```

### Server Won't Start

**Issue**: Port binding error

**Solution**: Ensure start command uses `$PORT`:
```
uvicorn api:app --host 0.0.0.0 --port $PORT
```

### 401 Unauthorized

**Issue**: API key not working

**Solution**: 
1. Check environment variable `API_KEY` is set in Render
2. Verify header is `x-api-key` (not `Authorization`)

### 500 Internal Server Error

**Issue**: Missing files

**Solution**: Ensure these files are in repository:
- `api.py`
- `src/feature_engineering.py`
- `src/anomaly_detection.py`
- `src/decision_engine.py`
- `reports/human_feature_profile.json`
- `reports/human_anomaly_thresholds.json`

---

## 📁 Required Files in Repository

```
your-repo/
├── api.py                              # Main API file
├── requirements.txt                    # Dependencies
├── render.yaml                         # Render config (optional)
├── src/
│   ├── __init__.py                     # Empty file
│   ├── feature_engineering.py
│   ├── anomaly_detection.py
│   └── decision_engine.py
└── reports/
    ├── human_feature_profile.json
    └── human_anomaly_thresholds.json
```

---

## 🌐 Public URL

After deployment, Render provides a URL like:
```
https://ai-voice-detection-api.onrender.com
```

Use this URL for:
- Official Endpoint Tester
- Hackathon submission
- Automated evaluation

---

## 💰 Cost Estimate

### Free Tier
- **Cost**: $0/month
- **Limitations**: 
  - Spins down after 15 min inactivity
  - Cold start ~30 seconds
  - 750 hours/month

### Starter Tier (Recommended)
- **Cost**: $7/month
- **Benefits**:
  - Always on (no spin down)
  - Fast cold start (<5 seconds)
  - Unlimited hours
  - Better for hackathon evaluation

---

## 🎯 Final Verification

Before submitting to hackathon:

1. ✅ Test with official Endpoint Tester UI
2. ✅ Verify response format is exact
3. ✅ Check latency < 2 seconds
4. ✅ Confirm API stays live for 24+ hours
5. ✅ Test with multiple audio samples

---

## 📞 Support

If deployment fails:
1. Check Render logs in Dashboard
2. Verify all files are in GitHub repo
3. Ensure environment variables are set
4. Test locally first: `uvicorn api:app --port 8000`

---

**Deployment Status**: Ready for Render ✅  
**Estimated Deploy Time**: 5-10 minutes  
**Public URL**: Provided by Render after deployment
