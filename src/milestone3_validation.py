import os
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
import matplotlib.pyplot as plt
from feature_engineering import FeatureExtractor
from anomaly_detection import AnomalyScorer

def run_validation():
    test_split_path = "e:/HCL/data/test_split.csv"
    profile_path = "e:/HCL/reports/human_feature_profile.json"
    
    if not os.path.exists(test_split_path) or not os.path.exists(profile_path):
        print("Required files not found. Ensure Milestones 1 & 2 are complete.")
        return

    df_test = pd.read_csv(test_split_path)
    # Use up to 100 samples for validation
    df_test = df_test.sample(min(100, len(df_test)), random_state=42)
    
    extractor = FeatureExtractor(sr=16000)
    scorer = AnomalyScorer(profile_path)
    
    validation_results = []
    anomaly_scores = []
    
    for idx, row in tqdm(df_test.iterrows(), total=len(df_test), desc="Validating Human Samples"):
        file_path = os.path.join("e:/HCL", row['file_path'])
        
        # 1. Feature Extraction
        feat = extractor.extract_all(file_path)
        if not feat:
            continue
            
        # Flatten features
        flat_feat = {}
        for k, v in feat.items():
            if isinstance(v, list):
                for i, val in enumerate(v):
                    flat_feat[f"{k}_{i}"] = val
            else:
                flat_feat[k] = v
        
        # 2. Anomaly Scoring
        score, reliability = scorer.score(flat_feat, snr=row.get('snr_db'), duration=row.get('duration_sec'))
        anomaly_scores.append(score)
        
        validation_results.append({
            "id": row['id'],
            "language": row['language'],
            "anomaly_score": score,
            "reliability": reliability,
            "snr_db": row.get('snr_db'),
            "duration_sec": row.get('duration_sec')
        })
        
    val_df = pd.DataFrame(validation_results)
    
    # 3. Threshold Calibration (95th percentile of human scores)
    threshold_95 = np.percentile(anomaly_scores, 95)
    threshold_99 = np.percentile(anomaly_scores, 99)
    
    thresholds = {
        "human_95th_percentile": float(threshold_95),
        "human_99th_percentile": float(threshold_99),
        "recommended_threshold": float(threshold_95)
    }
    
    # Save Thresholds
    with open("e:/HCL/reports/human_anomaly_thresholds.json", "w") as f:
        json.dump(thresholds, f, indent=4)
        
    # Save Validation Scores
    val_df.to_csv("e:/HCL/reports/anomaly_scores_human_validation.csv", index=False)
    
    # 4. Visualization
    plt.figure(figsize=(10, 6))
    plt.hist(anomaly_scores, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    plt.axvline(threshold_95, color='red', linestyle='dashed', linewidth=2, label=f'95th Percentile ({threshold_95:.2f})')
    plt.title('Distribution of Anomaly Scores for Human Speech')
    plt.xlabel('Anomaly Score')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.savefig("e:/HCL/reports/anomaly_score_distribution.png")
    
    print(f"Milestone 3 Validation Complete.")
    print(f"95th Percentile Threshold: {threshold_95:.4f}")
    print(f"Results saved to reports/")

if __name__ == "__main__":
    run_validation()
