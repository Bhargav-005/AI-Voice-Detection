"""
Production REST API for AI-Generated Voice Detection
Official Endpoint Tester Compatible - National Hackathon
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

from feature_engineering import FeatureExtractor
from anomaly_detection import AnomalyScorer
from decision_engine import DecisionEngine

# API Configuration
API_KEY = "HCL_AI_VOICE_DETECTION_2026"  # In production, use environment variable

app = FastAPI(
    title="AI-Generated Voice Detection API",
    description="Official Endpoint Tester Compatible - Forensic detection using statistical human speech profiling",
    version="1.0.0"
)

# Initialize components
extractor = FeatureExtractor(sr=16000)
scorer = AnomalyScorer("e:/HCL/reports/human_feature_profile.json")
engine = DecisionEngine("e:/HCL/reports/human_anomaly_thresholds.json")

# Request/Response Models (Official Endpoint Tester Format)
class DetectionRequest(BaseModel):
    language: str  # Metadata only - does not affect detection
    audio_format: str  # Metadata only - does not affect detection
    audio_base64_format: str  # The actual base64-encoded MP3 audio
    
class DetectionResponse(BaseModel):
    classification: str  # Only "HUMAN" or "AI_GENERATED"
    confidence: float    # 0.0 to 1.0

def map_to_minimal_response(decision: dict) -> dict:
    """
    Map internal decision to minimal public API response for automated evaluation.
    
    Mandatory Schema:
    - classification: "HUMAN" or "AI_GENERATED"
    - confidence: 0.0 to 1.0
    
    Mapping Rule: UNCERTAIN -> HUMAN with reduced confidence
    """
    internal_result = decision['result']
    
    # Map UNCERTAIN to HUMAN (ethical conservatism)
    if internal_result == "UNCERTAIN":
        classification = "HUMAN"
        confidence = min(decision['confidence'], 0.5)
    else:
        classification = internal_result
        confidence = decision['confidence']
    
    # Return only required fields for automated evaluation
    return {
        "classification": classification,
        "confidence": round(confidence, 3)
    }

# API Key Validation (x-api-key header)
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Voice Detection",
        "version": "1.0.0"
    }

# Main Detection Endpoint (Official Endpoint Tester Compatible)
@app.post("/detect", response_model=DetectionResponse)
async def detect_ai_voice(
    request: DetectionRequest,
    x_api_key: str = Depends(verify_api_key)
):
    """
    Detect if an audio sample is AI-generated or human speech.
    
    **Official Endpoint Tester Compatible**
    
    **Input**:
    - language: Metadata only (e.g., "en", "hi", "ta")
    - audio_format: Metadata only (e.g., "mp3", "wav")
    - audio_base64_format: Base64-encoded audio (MP3/WAV)
    
    **Output**:
    - classification: "HUMAN" or "AI_GENERATED"
    - confidence: 0.0 to 1.0
    """
    try:
        # Extract base64 audio (language and audio_format are metadata only)
        audio_base64 = request.audio_base64_format
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(audio_bytes)
        
        try:
            # Load and preprocess audio (librosa handles MP3/WAV automatically)
            y, sr = librosa.load(tmp_path, sr=16000)
            duration = len(y) / sr
            
            # Validate duration
            if duration < 0.3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Audio too short (minimum 0.3 seconds required)"
                )
            
            # Save as standardized WAV for feature extraction
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
            
            # Estimate SNR (simplified)
            rms = librosa.feature.rms(y=y)[0]
            signal_power = np.mean(rms**2)
            noise_power = np.min(rms**2)
            snr = 10 * np.log10(signal_power / (noise_power + 1e-10)) if noise_power > 0 else 50
            
            # Compute anomaly score
            anomaly_score, reliability = scorer.score(flat_features, snr=snr, duration=duration)
            
            # Get feature scores for explanation (internal only)
            feature_scores = scorer.calculate_raw_scores(flat_features)
            
            # Make decision (internal)
            decision = engine.decide(anomaly_score, reliability, feature_scores)
            
            # Map to minimal public API response (automated evaluation compatibility)
            public_response = map_to_minimal_response(decision)
            
            # Cleanup
            os.remove(tmp_path)
            if os.path.exists(wav_path):
                os.remove(wav_path)
            
            return DetectionResponse(**public_response)
            
        except HTTPException:
            # Re-raise HTTP exceptions
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise
        except Exception as e:
            # Cleanup on error
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

# System Info Endpoint
@app.get("/info")
async def system_info(x_api_key: str = Depends(verify_api_key)):
    """Get system information and statistics"""
    import json
    
    with open("e:/HCL/reports/human_anomaly_thresholds.json", 'r') as f:
        thresholds = json.load(f)
    
    return {
        "system": "AI-Generated Voice Detection",
        "approach": "Statistical forensic analysis",
        "endpoint_tester_compatible": True,
        "request_format": {
            "language": "Metadata only (e.g., 'en', 'hi', 'ta')",
            "audio_format": "Metadata only (e.g., 'mp3', 'wav')",
            "audio_base64_format": "Base64-encoded audio"
        },
        "response_format": {
            "classification": "HUMAN | AI_GENERATED",
            "confidence": "0.0 - 1.0"
        },
        "human_baseline": {
            "languages": ["Telugu", "Hindi", "Tamil", "Kannada", "Malayalam"],
            "samples": 500,
            "threshold_95th_percentile": thresholds['recommended_threshold']
        },
        "features": {
            "spectral": ["MFCCs (13)", "Centroid", "Bandwidth", "Flatness", "Rolloff"],
            "prosodic": ["F0", "Jitter", "Shimmer"],
            "temporal": ["ZCR", "Energy Entropy"]
        },
        "judge_statement": "Our system does not memorize AI voices. It learns what human speech is allowed to be and flags any speech that violates those statistically learned biological boundaries."
    }

if __name__ == "__main__":
    print("="*70)
    print("AI VOICE DETECTION API - OFFICIAL ENDPOINT TESTER COMPATIBLE")
    print("="*70)
    print(f"\nAPI Key: {API_KEY}")
    print("Header: x-api-key")
    print("\nRequest Format:")
    print("  POST /detect")
    print("  {")
    print('    "language": "en",')
    print('    "audio_format": "mp3",')
    print('    "audio_base64_format": "<BASE64_ENCODED_MP3>"')
    print("  }")
    print("\nResponse Format:")
    print("  {")
    print('    "classification": "HUMAN" | "AI_GENERATED",')
    print('    "confidence": 0.0 - 1.0')
    print("  }")
    print("\nAccess Swagger docs at: http://localhost:8000/docs")
    print("="*70)
    uvicorn.run(app, host="0.0.0.0", port=8000)
