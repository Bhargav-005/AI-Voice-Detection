# AI-Generated Voice Detection API

**Production-Ready REST API for National Hackathon Evaluation**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

---

## 🎯 Quick Deploy

### 1. Deploy to Render

```bash
# Clone/Push to GitHub
git clone <your-repo>
cd ai-voice-detection

# Deploy on Render
# 1. Go to https://render.com
# 2. New Web Service → Connect GitHub
# 3. Set environment variable: API_KEY=HCL_AI_VOICE_DETECTION_2026
# 4. Deploy
```

### 2. Verify Deployment

```bash
curl https://your-app.onrender.com/health
# Expected: {"status":"ok"}
```

---

## 📋 API Specification

### Endpoint: POST /detect

**Request**:
```json
{
  "language": "en",
  "audio_format": "mp3",
  "audio_base64_format": "<BASE64_ENCODED_MP3>"
}
```

**Headers**:
```
x-api-key: HCL_AI_VOICE_DETECTION_2026
Content-Type: application/json
```

**Response**:
```json
{
  "classification": "HUMAN" | "AI_GENERATED",
  "confidence": 0.0 - 1.0
}
```

---

## 🚀 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn api:app --reload --port 8000

# Test
curl http://localhost:8000/health
```

---

## 📊 System Performance

- **Accuracy**: 91.96%
- **Human Specificity**: 95.00%
- **Latency**: <2 seconds
- **Cold Start**: <5 seconds

---

## 🛡️ Features

✅ Official Endpoint Tester Compatible  
✅ Language-Agnostic Detection  
✅ Statistical Forensic Analysis  
✅ No Hard-Coded Thresholds  
✅ Ethical Conservatism (UNCERTAIN → HUMAN)  

---

## 📁 Repository Structure

```
├── api.py                      # Main API (deployment entry point)
├── requirements.txt            # Dependencies
├── src/
│   ├── feature_engineering.py
│   ├── anomaly_detection.py
│   └── decision_engine.py
└── reports/
    ├── human_feature_profile.json
    └── human_anomaly_thresholds.json
```

---

## 🔐 Environment Variables

| Variable | Value | Required |
|----------|-------|----------|
| `API_KEY` | `HCL_AI_VOICE_DETECTION_2026` | Yes |
| `PORT` | Auto-set by Render | No |

---

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- [Endpoint Tester Compatibility](ENDPOINT_TESTER_COMPATIBILITY.md)

---

## 🎓 Technical Approach

**Core Innovation**: Statistical forensic analysis without AI memorization

> "Our system does not memorize AI voices. It learns what human speech is allowed to be and flags any speech that violates those statistically learned biological boundaries."

**Detection Method**:
1. Extract 38+ acoustic features (spectral, prosodic, temporal)
2. Compare against human speech baseline (500 samples, 5 languages)
3. Calculate anomaly score using Z-score analysis
4. Classify based on 95th percentile threshold (1.1419)

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render web service created
- [ ] Environment variable `API_KEY` set
- [ ] Health check configured (`/health`)
- [ ] Public URL obtained
- [ ] Official Endpoint Tester passes

---

## 🆘 Support

**Deployment Issues**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)  
**API Issues**: Check Render logs in dashboard  
**Testing**: Use [test_endpoint_tester.py](test_endpoint_tester.py)

---

## 📞 Contact

**API Version**: 1.0.0  
**Status**: Production Ready ✅  
**Platform**: Render (HTTPS)  
**Evaluation**: Official Endpoint Tester Compatible

---

**Ready for National Hackathon Evaluation** 🏆
