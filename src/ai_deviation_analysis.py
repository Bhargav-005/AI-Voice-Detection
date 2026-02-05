"""
AI Deviation Analysis Module
Analyzes AI-generated speech against the established human baseline.
"""
import os
import pandas as pd
import numpy as np
import json
import librosa
from tqdm import tqdm
import matplotlib.pyplot as plt
from feature_engineering import FeatureExtractor
from anomaly_detection import AnomalyScorer

def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 to WAV format"""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")
        return True
    except Exception as e:
        print(f"Error converting {mp3_path}: {e}")
        return False

def analyze_ai_samples():
    """Analyze AI-generated speech samples"""
    
    # Paths
    ai_dir = "e:/HCL/data/synthetic/gtts"
    profile_path = "e:/HCL/reports/human_feature_profile.json"
    thresholds_path = "e:/HCL/reports/human_anomaly_thresholds.json"
    
    if not os.path.exists(profile_path):
        print("Human profile not found. Run Milestones 1-3 first.")
        return
    
    # Load thresholds
    with open(thresholds_path, 'r') as f:
        thresholds = json.load(f)
    human_threshold = thresholds['recommended_threshold']
    
    # Initialize
    extractor = FeatureExtractor(sr=16000)
    scorer = AnomalyScorer(profile_path)
    
    ai_results = []
    
    # Process AI samples
    mp3_files = [f for f in os.listdir(ai_dir) if f.endswith('.mp3')]
    
    for mp3_file in tqdm(mp3_files, desc="Analyzing AI samples"):
        mp3_path = os.path.join(ai_dir, mp3_file)
        
        try:
            # Load MP3 directly with librosa
            y, sr = librosa.load(mp3_path, sr=16000)
            duration = len(y) / sr
            
            # Save as WAV for feature extraction
            wav_path = mp3_path.replace('.mp3', '.wav')
            import soundfile as sf
            sf.write(wav_path, y, 16000)
            
            # Extract features
            feat = extractor.extract_all(wav_path)
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
            
            # Get audio duration and estimate SNR (already loaded above)
            # duration already calculated
            
            # Compute anomaly score
            anomaly_score, reliability = scorer.score(flat_feat, snr=50, duration=duration)
            
            # Categorize feature scores
            feature_scores = scorer.calculate_raw_scores(flat_feat)
            
            spectral_keys = [k for k in feature_scores.keys() if 'mfcc' in k or 'centroid' in k or 'bandwidth' in k or 'flatness' in k or 'rolloff' in k]
            prosodic_keys = [k for k in feature_scores.keys() if 'f0' in k or 'jitter' in k or 'shimmer' in k]
            temporal_keys = [k for k in feature_scores.keys() if 'zcr' in k or 'energy_entropy' in k]
            
            spectral_score = np.mean([feature_scores[k] for k in spectral_keys]) if spectral_keys else 0
            prosodic_score = np.mean([feature_scores[k] for k in prosodic_keys]) if prosodic_keys else 0
            temporal_score = np.mean([feature_scores[k] for k in temporal_keys]) if temporal_keys else 0
            
            ai_results.append({
                "sample_id": mp3_file.replace('.mp3', ''),
                "anomaly_score": anomaly_score,
                "reliability": reliability,
                "spectral_deviation": spectral_score,
                "prosodic_deviation": prosodic_score,
                "temporal_deviation": temporal_score,
                "duration_sec": duration,
                "exceeds_threshold": anomaly_score > human_threshold
            })
            
        except Exception as e:
            print(f"Error processing {mp3_file}: {e}")
            continue
    
    # Save results
    if len(ai_results) == 0:
        print("No AI samples were successfully processed.")
        return None
        
    ai_df = pd.DataFrame(ai_results)
    ai_df.to_csv("e:/HCL/reports/ai_anomaly_scores.csv", index=False)
    
    # Generate comparison visualization
    generate_comparison_plot(ai_df, human_threshold)
    
    # Print summary
    print(f"\n{'='*60}")
    print("AI DEVIATION ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"Total AI samples analyzed: {len(ai_df)}")
    print(f"Human threshold (95th percentile): {human_threshold:.4f}")
    print(f"\nAI Sample Statistics:")
    print(f"  Mean anomaly score: {ai_df['anomaly_score'].mean():.4f}")
    print(f"  Std deviation: {ai_df['anomaly_score'].std():.4f}")
    print(f"  Min score: {ai_df['anomaly_score'].min():.4f}")
    print(f"  Max score: {ai_df['anomaly_score'].max():.4f}")
    print(f"\nSamples exceeding human threshold: {ai_df['exceeds_threshold'].sum()} ({ai_df['exceeds_threshold'].sum()/len(ai_df)*100:.1f}%)")
    print(f"\nDominant Violation Categories:")
    print(f"  Spectral: {ai_df['spectral_deviation'].mean():.4f}")
    print(f"  Prosodic: {ai_df['prosodic_deviation'].mean():.4f}")
    print(f"  Temporal: {ai_df['temporal_deviation'].mean():.4f}")
    print(f"{'='*60}\n")
    
    return ai_df

def generate_comparison_plot(ai_df, human_threshold):
    """Generate AI vs Human comparison visualization"""
    
    # Load human validation scores
    human_df = pd.read_csv("e:/HCL/reports/anomaly_scores_human_validation.csv")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('AI vs Human Speech: Anomaly Score Comparison', fontsize=16, fontweight='bold')
    
    # 1. Score Distribution Comparison
    ax1 = axes[0, 0]
    ax1.hist(human_df['anomaly_score'], bins=20, alpha=0.6, label='Human', color='#4ECDC4', edgecolor='black')
    ax1.hist(ai_df['anomaly_score'], bins=20, alpha=0.6, label='AI-Generated', color='#FF6B6B', edgecolor='black')
    ax1.axvline(human_threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({human_threshold:.2f})')
    ax1.set_xlabel('Anomaly Score')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Score Distribution: Human vs AI')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Box Plot Comparison
    ax2 = axes[0, 1]
    data_to_plot = [human_df['anomaly_score'], ai_df['anomaly_score']]
    bp = ax2.boxplot(data_to_plot, labels=['Human', 'AI-Generated'], patch_artist=True)
    bp['boxes'][0].set_facecolor('#4ECDC4')
    bp['boxes'][1].set_facecolor('#FF6B6B')
    ax2.axhline(human_threshold, color='red', linestyle='--', linewidth=2, label='Threshold')
    ax2.set_ylabel('Anomaly Score')
    ax2.set_title('Score Distribution Comparison')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Category Deviation Comparison
    ax3 = axes[1, 0]
    categories = ['Spectral', 'Prosodic', 'Temporal']
    ai_means = [
        ai_df['spectral_deviation'].mean(),
        ai_df['prosodic_deviation'].mean(),
        ai_df['temporal_deviation'].mean()
    ]
    x_pos = np.arange(len(categories))
    bars = ax3.bar(x_pos, ai_means, color=['#FF6B6B', '#FFA07A', '#FFD700'], edgecolor='black')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(categories)
    ax3.set_ylabel('Mean Deviation (Z-score)')
    ax3.set_title('AI Speech: Category-Level Deviations')
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Detection Performance
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    human_below = len(human_df[human_df['anomaly_score'] <= human_threshold])
    human_above = len(human_df[human_df['anomaly_score'] > human_threshold])
    ai_below = len(ai_df[ai_df['anomaly_score'] <= human_threshold])
    ai_above = len(ai_df[ai_df['anomaly_score'] > human_threshold])
    
    summary_data = [
        ['Category', 'Below Threshold', 'Above Threshold', 'Total'],
        ['Human', str(human_below), str(human_above), str(len(human_df))],
        ['AI-Generated', str(ai_below), str(ai_above), str(len(ai_df))],
        ['', '', '', ''],
        ['Metrics', 'Value', '', ''],
        ['Human Specificity', f'{human_below/len(human_df)*100:.1f}%', '', ''],
        ['AI Detection Rate', f'{ai_above/len(ai_df)*100:.1f}%', '', '']
    ]
    
    table = ax4.table(cellText=summary_data, cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header
    for i in range(4):
        table[(0, i)].set_facecolor('#4ECDC4')
        table[(0, i)].set_text_props(weight='bold')
        table[(4, i)].set_facecolor('#FFE66D')
        table[(4, i)].set_text_props(weight='bold')
    
    ax4.set_title('Detection Performance Summary', fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('e:/HCL/reports/ai_vs_human_anomaly_comparison.png', dpi=300, bbox_inches='tight')
    print("Comparison visualization saved!")

if __name__ == "__main__":
    analyze_ai_samples()
