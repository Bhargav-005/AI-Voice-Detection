import json
import numpy as np
import os

class AnomalyScorer:
    def __init__(self, profile_path):
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Profile not found at {profile_path}")
            
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)
        
        self.means = self.profile['mean']
        self.stds = self.profile['std']

    def calculate_raw_scores(self, sample_features):
        """
        Compute z-scores for all features.
        """
        feature_scores = {}
        for feat_name, value in sample_features.items():
            if feat_name in self.means and self.stds[feat_name] > 0:
                z = (value - self.means[feat_name]) / self.stds[feat_name]
                feature_scores[feat_name] = abs(z)
        return feature_scores

    def score(self, sample_features, snr=None, duration=None):
        """
        Compute a reliability-aware anomaly index.
        """
        feature_scores = self.calculate_raw_scores(sample_features)
        if not feature_scores:
            return 0.0, 0.0
            
        # Group scores by category
        spectral_keys = [k for k in feature_scores.keys() if 'mfcc' in k or 'centroid' in k or 'bandwidth' in k or 'flatness' in k or 'rolloff' in k]
        prosodic_keys = [k for k in feature_scores.keys() if 'f0' in k or 'jitter' in k or 'shimmer' in k]
        temporal_keys = [k for k in feature_scores.keys() if 'zcr' in k or 'energy_entropy' in k]
        
        spectral_score = np.mean([feature_scores[k] for k in spectral_keys]) if spectral_keys else 0
        prosodic_score = np.mean([feature_scores[k] for k in prosodic_keys]) if prosodic_keys else 0
        temporal_score = np.mean([feature_scores[k] for k in temporal_keys]) if temporal_keys else 0
        
        # Combined anomaly score (forensic mean)
        base_anomaly_score = (spectral_score + prosodic_score + temporal_score) / 3
        
        # Reliability Assessment
        # SNR < 20dB or duration < 1.0s reduces reliability
        reliability = 1.0
        if snr is not None:
            # Linear penalty for low SNR below 30dB
            reliability *= np.clip(snr / 30.0, 0.5, 1.0)
        if duration is not None:
            # Linear penalty for short duration below 2s
            reliability *= np.clip(duration / 2.0, 0.5, 1.0)
            
        return float(base_anomaly_score), float(reliability)

def demo_anomaly_scoring():
    profile_path = "e:/HCL/reports/human_feature_profile.json"
    try:
        scorer = AnomalyScorer(profile_path)
    except FileNotFoundError:
        print("Profile not found. Please ensure Milestone 2 is complete.")
        return
        
    # Example "human-like" behavior
    human_mock = {
        "jitter": 0.04,
        "shimmer": 0.16,
        "f0_mean": 300.0,
        "centroid_mean": 1100.0
    }
    
    # Example "synthetic" behavior: Zero jitter and shimmer (perfectly clean)
    synthetic_mock = {
        "jitter": 0.001,
        "shimmer": 0.01,
        "f0_mean": 300.0,
        "centroid_mean": 1100.0
    }
    
    h_score, h_rel = scorer.score(human_mock, snr=45, duration=5.0)
    s_score, s_rel = scorer.score(synthetic_mock, snr=45, duration=5.0)
    
    print(f"Human Mock Anomaly Score: {h_score:.4f} (Reliability: {h_rel:.2f})")
    print(f"Synthetic Mock Anomaly Score: {s_score:.4f} (Reliability: {s_rel:.2f})")

if __name__ == "__main__":
    demo_anomaly_scoring()
