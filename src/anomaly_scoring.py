import json
import numpy as np
import os
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any

# Setup logging
os.makedirs("e:/HCL/logs", exist_ok=True)
logging.basicConfig(
    filename="e:/HCL/logs/anomaly_inference.log",
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class AnomalyScorer:
    def __init__(self, profile_path: str, thresholds_path: str = "e:/HCL/reports/human_anomaly_thresholds.json"):
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Profile not found at {profile_path}")
            
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)
        
        self.means = self.profile['mean']
        self.stds = self.profile['std']
        
        # Load calibrated thresholds if they exist
        self.thresholds = None
        if os.path.exists(thresholds_path):
            with open(thresholds_path, 'r') as f:
                self.thresholds = json.load(f)
        
        # Define feature categories
        self.categories = {
            "spectral": ["mfcc_mean", "mfcc_std", "centroid_mean", "bandwidth_mean", "flatness_mean", "rolloff_mean"],
            "prosodic": ["f0_mean", "f0_std", "jitter", "shimmer"],
            "temporal": ["zcr_mean", "energy_entropy"]
        }

    def _get_category_for_feature(self, feat_name: str) -> str:
        for cat, prefixes in self.categories.items():
            for prefix in prefixes:
                if feat_name.startswith(prefix):
                    return cat
        return "other"

    def compute_reliability_factor(self, snr: float, duration: float) -> float:
        """
        Compute a reliability factor between 0 and 1.
        Low SNR or very short duration reduces reliability.
        """
        # SNR factor: 1.0 above 20dB, scales down to 0.5 at 0dB (clamped)
        snr_factor = np.clip((snr / 20.0) * 0.5 + 0.5, 0.5, 1.0)
        
        # Duration factor: 1.0 above 3s, scales down to 0.5 at 0.5s
        duration_factor = np.clip((duration / 3.0) * 0.5 + 0.5, 0.5, 1.0)
        
        return float(snr_factor * duration_factor)

    def score(self, sample_features: Dict[str, float], snr: float = 30.0, duration: float = 3.0) -> Dict[str, Any]:
        """
        Compute a comprehensive anomaly report.
        """
        deviations = {}
        category_scores = {"spectral": [], "prosodic": [], "temporal": [], "other": []}
        
        for feat_name, value in sample_features.items():
            if feat_name in self.means and self.stds.get(feat_name, 0) > 0:
                z = (value - self.means[feat_name]) / self.stds[feat_name]
                abs_z = abs(float(z))
                deviations[feat_name] = abs_z
                
                cat = self._get_category_for_feature(feat_name)
                category_scores[cat].append(abs_z)
        
        # Aggregate category scores
        cat_summaries = {}
        all_z = []
        for cat, scores in category_scores.items():
            if scores:
                cat_summaries[f"{cat}_deviation"] = float(np.mean(scores))
                all_z.extend(scores)
            else:
                cat_summaries[f"{cat}_deviation"] = 0.0
                
        raw_anomaly_score = float(np.mean(all_z)) if all_z else 0.0
        reliability = self.compute_reliability_factor(snr, duration)
        
        final_score = raw_anomaly_score * reliability
        
        # Interpretation based on calibrated thresholds
        interpretation = "Analyzing..."
        if self.thresholds:
            t95 = self.thresholds['human_variability_95th']
            t99 = self.thresholds['human_variability_99th']
            
            if final_score <= t95:
                interpretation = "Within expected human variability"
            elif final_score <= t99:
                interpretation = "Near human limit (review recommended)"
            else:
                interpretation = "Significant anomaly detected - potential non-human behavior"
        else:
            # Fallback if thresholds not yet calibrated
            if final_score > 3.0:
                interpretation = "Significant anomaly detected"
            else:
                interpretation = "Within normal range"
        
        report = {
            "final_anomaly_score": round(final_score, 4),
            "raw_anomaly_score": round(raw_anomaly_score, 4),
            "reliability_factor": round(reliability, 2),
            "spectral_deviation": round(cat_summaries["spectral_deviation"], 4),
            "prosodic_deviation": round(cat_summaries["prosodic_deviation"], 4),
            "temporal_deviation": round(cat_summaries["temporal_deviation"], 4),
            "interpretation": interpretation
        }
        
        # Log inference
        logging.info(f"Inference: score={report['final_anomaly_score']}, reliability={report['reliability_factor']}, interpretation='{interpretation}'")
        
        return report

def run_anomaly_tests():
    # This is a basic test script to verify the logic
    profile_path = "e:/HCL/reports/human_feature_profile.json"
    if not os.path.exists(profile_path):
        print("Profile not found. Please run src/feature_engineering.py first.")
        return
        
    scorer = AnomalyScorer(profile_path)
    
    # Mock a "perfectly human" sample (using means)
    human_mock = scorer.means
    report = scorer.score(human_mock, snr=40, duration=5.0)
    print("\n--- Human-like Sample Report ---")
    print(json.dumps(report, indent=2))
    
    # Mock an "anomalous" sample (shifting some features)
    anomaly_mock = human_mock.copy()
    anomaly_mock["jitter"] = 0.0  # Too clean
    anomaly_mock["shimmer"] = 0.0 # Too clean
    anomaly_mock["f0_std"] = 1.0  # Robotic monotone
    
    report_anom = scorer.score(anomaly_mock, snr=40, duration=5.0)
    print("\n--- Anomalous Sample Report ---")
    print(json.dumps(report_anom, indent=2))

if __name__ == "__main__":
    run_anomaly_tests()
