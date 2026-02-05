"""
Decision Engine for AI-Generated Voice Detection
Makes final classification decisions based on anomaly scores and reliability.
"""
import json
import numpy as np

class DecisionEngine:
    def __init__(self, thresholds_path="e:/HCL/reports/human_anomaly_thresholds.json"):
        """Initialize decision engine with calibrated thresholds"""
        with open(thresholds_path, 'r') as f:
            thresholds = json.load(f)
        
        self.human_threshold = thresholds['recommended_threshold']
        self.min_reliability = 0.7  # Minimum reliability for confident decisions
        
    def calculate_confidence(self, anomaly_score, reliability, feature_scores):
        """
        Calculate confidence score based on:
        - Distance from threshold
        - Reliability factor
        - Feature group agreement
        """
        # Distance-based confidence
        if anomaly_score <= self.human_threshold:
            # For human classification: how far below threshold
            distance_factor = 1.0 - (anomaly_score / self.human_threshold)
        else:
            # For AI classification: how far above threshold
            distance_factor = min(1.0, (anomaly_score - self.human_threshold) / self.human_threshold)
        
        # Feature group agreement (how many categories show deviation)
        spectral_keys = [k for k in feature_scores.keys() if 'mfcc' in k or 'centroid' in k or 'bandwidth' in k or 'flatness' in k or 'rolloff' in k]
        prosodic_keys = [k for k in feature_scores.keys() if 'f0' in k or 'jitter' in k or 'shimmer' in k]
        temporal_keys = [k for k in feature_scores.keys() if 'zcr' in k or 'energy_entropy' in k]
        
        spectral_score = np.mean([feature_scores[k] for k in spectral_keys]) if spectral_keys else 0
        prosodic_score = np.mean([feature_scores[k] for k in prosodic_keys]) if prosodic_keys else 0
        temporal_score = np.mean([feature_scores[k] for k in temporal_keys]) if temporal_keys else 0
        
        # Count how many categories exceed threshold (>1.5 z-score)
        deviating_categories = sum([
            spectral_score > 1.5,
            prosodic_score > 1.5,
            temporal_score > 1.5
        ])
        
        agreement_factor = deviating_categories / 3.0
        
        # Combined confidence
        confidence = (distance_factor * 0.5 + reliability * 0.3 + agreement_factor * 0.2)
        return float(np.clip(confidence, 0, 1))
    
    def calculate_risk_level(self, anomaly_score, reliability):
        """
        Calculate risk level based on score and reliability
        """
        if reliability < self.min_reliability:
            return "HIGH"  # Low reliability = high risk
        
        if anomaly_score <= self.human_threshold:
            return "LOW"  # Within human range
        elif anomaly_score <= self.human_threshold * 1.5:
            return "MEDIUM"  # Moderately above threshold
        else:
            return "HIGH"  # Significantly above threshold (strong AI signal)
    
    def generate_explanation(self, anomaly_score, feature_scores, reliability):
        """
        Generate human-readable explanation for the decision
        """
        explanations = {}
        
        # Categorize feature scores
        spectral_keys = [k for k in feature_scores.keys() if 'mfcc' in k or 'centroid' in k or 'bandwidth' in k or 'flatness' in k or 'rolloff' in k]
        prosodic_keys = [k for k in feature_scores.keys() if 'f0' in k or 'jitter' in k or 'shimmer' in k]
        temporal_keys = [k for k in feature_scores.keys() if 'zcr' in k or 'energy_entropy' in k]
        
        spectral_score = np.mean([feature_scores[k] for k in spectral_keys]) if spectral_keys else 0
        prosodic_score = np.mean([feature_scores[k] for k in prosodic_keys]) if prosodic_keys else 0
        temporal_score = np.mean([feature_scores[k] for k in temporal_keys]) if temporal_keys else 0
        
        # Spectral explanation
        if spectral_score > 1.5:
            explanations['spectral'] = f"Spectral features deviate {spectral_score:.2f}σ from human baseline (MFCC patterns show artificial smoothness)"
        elif spectral_score > 1.0:
            explanations['spectral'] = f"Mild spectral deviation detected ({spectral_score:.2f}σ)"
        else:
            explanations['spectral'] = "Spectral features within human range"
        
        # Prosodic explanation
        if prosodic_score > 1.5:
            if 'jitter' in feature_scores and feature_scores['jitter'] > 2.0:
                explanations['prosodic'] = f"Pitch jitter below biological human range ({prosodic_score:.2f}σ deviation)"
            elif 'shimmer' in feature_scores and feature_scores['shimmer'] > 2.0:
                explanations['prosodic'] = f"Amplitude shimmer below biological human range ({prosodic_score:.2f}σ deviation)"
            else:
                explanations['prosodic'] = f"Prosodic features deviate {prosodic_score:.2f}σ from human baseline"
        else:
            explanations['prosodic'] = "Prosodic features within human range"
        
        # Temporal explanation
        if temporal_score > 1.5:
            explanations['temporal'] = f"Temporal patterns deviate {temporal_score:.2f}σ from human baseline (unnatural rhythm)"
        else:
            explanations['temporal'] = "Temporal features within human range"
        
        # Decision note
        deviating_count = sum([spectral_score > 1.5, prosodic_score > 1.5, temporal_score > 1.5])
        if deviating_count >= 2:
            explanations['decision_note'] = "Multiple independent feature categories show significant deviations"
        elif deviating_count == 1:
            explanations['decision_note'] = "Single category deviation detected"
        else:
            explanations['decision_note'] = "All feature categories within expected human range"
        
        # Reliability note
        if reliability < self.min_reliability:
            explanations['quality_warning'] = f"Low signal quality (reliability: {reliability:.2f}) - decision confidence reduced"
        
        return explanations
    
    def decide(self, anomaly_score, reliability, feature_scores):
        """
        Make final classification decision
        
        Returns:
            dict with keys: result, confidence, risk_level, explanations
        """
        # Decision logic
        if anomaly_score <= self.human_threshold:
            result = "HUMAN"
        elif anomaly_score > self.human_threshold and reliability >= self.min_reliability:
            result = "AI_GENERATED"
        else:
            result = "UNCERTAIN"
        
        # Calculate confidence and risk
        confidence = self.calculate_confidence(anomaly_score, reliability, feature_scores)
        risk_level = self.calculate_risk_level(anomaly_score, reliability)
        
        # Generate explanations
        explanations = self.generate_explanation(anomaly_score, feature_scores, reliability)
        
        # Signal quality assessment
        if reliability >= 0.9:
            signal_quality = "EXCELLENT"
        elif reliability >= 0.8:
            signal_quality = "GOOD"
        elif reliability >= 0.7:
            signal_quality = "FAIR"
        else:
            signal_quality = "POOR"
        
        return {
            "result": result,
            "confidence": round(confidence, 3),
            "risk_level": risk_level,
            "signal_quality": signal_quality,
            "anomaly_score": round(anomaly_score, 4),
            "reliability": round(reliability, 3),
            "threshold": round(self.human_threshold, 4),
            "explanations": explanations
        }

def demo_decision_engine():
    """Demo the decision engine"""
    engine = DecisionEngine()
    
    # Test case 1: Clear human
    print("Test Case 1: Clear Human Speech")
    print("="*60)
    decision = engine.decide(
        anomaly_score=0.75,
        reliability=0.95,
        feature_scores={'jitter': 0.5, 'shimmer': 0.6, 'mfcc_mean_0': 0.4}
    )
    print(json.dumps(decision, indent=2))
    
    # Test case 2: Clear AI
    print("\n\nTest Case 2: Clear AI-Generated Speech")
    print("="*60)
    decision = engine.decide(
        anomaly_score=1.85,
        reliability=0.92,
        feature_scores={'jitter': 3.5, 'shimmer': 2.8, 'mfcc_mean_0': 1.2, 'zcr_mean': 2.5}
    )
    print(json.dumps(decision, indent=2))
    
    # Test case 3: Uncertain (low quality)
    print("\n\nTest Case 3: Uncertain (Low Quality)")
    print("="*60)
    decision = engine.decide(
        anomaly_score=1.25,
        reliability=0.55,
        feature_scores={'jitter': 1.8, 'shimmer': 1.5}
    )
    print(json.dumps(decision, indent=2))

if __name__ == "__main__":
    demo_decision_engine()
