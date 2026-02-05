import os
import librosa
import numpy as np
import pandas as pd
import json
from tqdm import tqdm
from scipy.stats import entropy

class FeatureExtractor:
    def __init__(self, sr=16000):
        self.sr = sr

    def extract_prosodic_features(self, y):
        # F0 extraction using yin
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        valid_f0 = f0[~np.isnan(f0)]
        
        if len(valid_f0) < 2:
            return {
                "f0_mean": 0, "f0_std": 0, "jitter": 0, "shimmer": 0
            }
        
        f0_mean = np.mean(valid_f0)
        f0_std = np.std(valid_f0)
        
        # Jitter (local): average absolute difference between consecutive periods divided by average period
        # Periods are 1/f0
        periods = 1.0 / valid_f0
        jitter = np.mean(np.abs(np.diff(periods))) / np.mean(periods) if len(periods) > 1 else 0
        
        # Shimmer: variation in peak amplitudes
        # Simple amplitude shimmer: mean absolute difference between peaks
        # Let's use the RMS energy over voiced segments as a proxy or find local peaks
        # Here we use RMS energy of the voiced frames
        rms = librosa.feature.rms(y=y)[0]
        voiced_rms = rms[voiced_flag > 0.5] if any(voiced_flag > 0.5) else []
        if len(voiced_rms) > 1:
            shimmer = np.mean(np.abs(np.diff(voiced_rms))) / np.mean(voiced_rms)
        else:
            shimmer = 0
            
        return {
            "f0_mean": float(f0_mean),
            "f0_std": float(f0_std),
            "jitter": float(jitter),
            "shimmer": float(shimmer)
        }

    def extract_spectral_features(self, y):
        # MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=self.sr, n_mfcc=13)
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.std(mfccs, axis=1)
        
        # Spectral Centroid
        centroid = librosa.feature.spectral_centroid(y=y, sr=self.sr)[0]
        # Spectral Bandwidth
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=self.sr)[0]
        # Flatness
        flatness = librosa.feature.spectral_flatness(y=y)[0]
        # Rolloff
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=self.sr)[0]
        
        return {
            "mfcc_mean": mfcc_mean.tolist(),
            "mfcc_std": mfcc_std.tolist(),
            "centroid_mean": float(np.mean(centroid)),
            "bandwidth_mean": float(np.mean(bandwidth)),
            "flatness_mean": float(np.mean(flatness)),
            "rolloff_mean": float(np.mean(rolloff))
        }

    def extract_temporal_features(self, y):
        # ZCR
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        # Energy Entropy
        # Split into frames and calculate entropy of energy
        rms = librosa.feature.rms(y=y)[0]
        energy = rms**2
        if np.sum(energy) > 0:
            prob = energy / np.sum(energy)
            eng_entropy = entropy(prob)
        else:
            eng_entropy = 0
            
        return {
            "zcr_mean": float(np.mean(zcr)),
            "energy_entropy": float(eng_entropy)
        }

    def extract_all(self, file_path):
        y, _ = librosa.load(file_path, sr=self.sr)
        if len(y) == 0:
             return None
             
        features = {}
        features.update(self.extract_spectral_features(y))
        features.update(self.extract_prosodic_features(y))
        features.update(self.extract_temporal_features(y))
        
        return features

def main():
    metadata_path = "e:/HCL/data/train_split.csv"
    if not os.path.exists(metadata_path):
        print("Metadata not found. Run Milestone 1 first.")
        return
        
    df = pd.read_csv(metadata_path)
    extractor = FeatureExtractor(sr=16000)
    
    all_features = []
    
    # Let's process a subset for profiling if it's too many, 
    # but 400 samples (80% of 500) is fine.
    # Limit samples for speed during milestone demo
    df = df.sample(min(50, len(df)), random_state=42)
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Extracting features"):
        try:
            file_path = os.path.join("e:/HCL", row['file_path'])
            feat = extractor.extract_all(file_path)
            if feat:
                # Flatten MFCCs
                flat_feat = {}
                for k, v in feat.items():
                    if isinstance(v, list):
                        for i, val in enumerate(v):
                            flat_feat[f"{k}_{i}"] = val
                    else:
                        flat_feat[k] = v
                all_features.append(flat_feat)
        except KeyboardInterrupt:
            print("Interrupted. Saving partial results...")
            break
        except Exception as e:
            print(f"Error processing {row['file_path']}: {e}")
            continue
            
    feat_df = pd.DataFrame(all_features)
    
    # Calculate Profile Statistics
    profile = {
        "mean": feat_df.mean().to_dict(),
        "std": feat_df.std().to_dict(),
        "min": feat_df.min().to_dict(),
        "max": feat_df.max().to_dict(),
        "q1": feat_df.quantile(0.25).to_dict(),
        "q3": feat_df.quantile(0.75).to_dict()
    }
    
    # Save Profile
    os.makedirs("e:/HCL/reports", exist_ok=True)
    with open("e:/HCL/reports/human_feature_profile.json", "w") as f:
        json.dump(profile, f, indent=4)
        
    print("Milestone 2: Human Speech Profile generated.")

if __name__ == "__main__":
    main()
