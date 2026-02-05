"""
Production REST API for AI-Generated Voice Detection
Deployment-ready with environment variable configuration
"""
from fastapi import FastAPI, HTTPException, Depends, status, Header
from pydantic import BaseModel
import base64
import os
import tempfile
import librosa
import soundfile as sf
import uvicorn
import numpy as np

from src.feature_engineering import FeatureExtractor
from src.anomaly_detection import AnomalyScorer
from src.decision_engine import DecisionEngine

# API Configuration from environment
API_KEY = os.getenv("API_KEY", "HCL_AI_VOICE_DETECTION_2026")

app = FastAPI(
    title="AI-Generated Voice Detection API",
    description="Official Endpoint Tester Compatible - Forensic detection using statistical human speech profiling",
    version="1.0.0"
)

# Initialize components with absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(BASE_DIR, "reports", "human_feature_profile.json")
THRESHOLD_PATH = os.path.join(BASE_DIR, "reports", "human_anomaly_thresholds.json")

extractor = FeatureExtractor(sr=16000)
scorer = AnomalyScorer(PROFILE_PATH)
engine = DecisionEngine(THRESHOLD_PATH)

# Request/Response Models
class DetectionRequest(BaseModel):
    language: str  # Metadata only
    audio_format: str  # Metadata only
    audio_base64_format: str  # Actual audio data
    
class DetectionResponse(BaseModel):
    classification: str  # "HUMAN" or "AI_GENERATED"
    confidence: float    # 0.0 to 1.0

def map_to_minimal_response(decision: dict) -> dict:
    """Map internal decision to minimal public response"""
    internal_result = decision['result']
    
    if internal_result == "UNCERTAIN":
        classification = "HUMAN"
        confidence = min(decision['confidence'], 0.5)
    else:
        classification = internal_result
        confidence = decision['confidence']
    
    return {
        "classification": classification,
        "confidence": round(confidence, 3)
    }

# API Key Validation
async def verify_api_key(x_api_key: str = Header(None)):
    """Validate API key from x-api-key header"""
    if x_api_key is None or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return x_api_key

# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification"""
    return {"status": "ok"}

# Main Detection Endpoint
@app.post("/detect", response_model=DetectionResponse)
async def detect_ai_voice(
    request: DetectionRequest,
    x_api_key: str = Depends(verify_api_key)
):
    """
    Detect if audio is AI-generated or human speech.
    
    Official Endpoint Tester Compatible
    """
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_base64_format)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(audio_bytes)
        
        try:
            # Load and preprocess audio
            y, sr = librosa.load(tmp_path, sr=16000)
            duration = len(y) / sr
            
            if duration < 0.3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Audio too short (minimum 0.3 seconds required)"
                )
            
            # Save as WAV for feature extraction
            wav_path = tmp_path.replace('.mp3', '_processed.wav')
            sf.write(wav_path, y, 16000)
            
            # Extract features
            features = extractor.extract_all(wav_path)
            if not features:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to extract features from audio"
                )
            
            # Flatten features
            flat_features = {}
            for k, v in features.items():
                if isinstance(v, list):
                    for i, val in enumerate(v):
                        flat_features[f"{k}_{i}"] = val
                else:
                    flat_features[k] = v
            
            # Estimate SNR
            rms = librosa.feature.rms(y=y)[0]
            signal_power = np.mean(rms**2)
            noise_power = np.min(rms**2)
            snr = 10 * np.log10(signal_power / (noise_power + 1e-10)) if noise_power > 0 else 50
            
            # Compute anomaly score
            anomaly_score, reliability = scorer.score(flat_features, snr=snr, duration=duration)
            
            # Get feature scores
            feature_scores = scorer.calculate_raw_scores(flat_features)
            
            # Make decision
            decision = engine.decide(anomaly_score, reliability, feature_scores)
            
            # Map to minimal response
            public_response = map_to_minimal_response(decision)
            
            # Cleanup
            os.remove(tmp_path)
            if os.path.exists(wav_path):
                os.remove(wav_path)
            
            return DetectionResponse(**public_response)
            
        except HTTPException:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing error: {str(e)}"
            )
            
    except base64.binascii.Error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 encoding"
        )

# Info endpoint (optional, for debugging)
@app.get("/info")
async def system_info(x_api_key: str = Depends(verify_api_key)):
    """System information"""
    import json
    
    with open(THRESHOLD_PATH, 'r') as f:
        thresholds = json.load(f)
    
    return {
        "system": "AI-Generated Voice Detection",
        "version": "1.0.0",
        "endpoint_tester_compatible": True,
        "threshold": thresholds['recommended_threshold']
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
