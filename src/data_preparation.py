import os
import librosa
import numpy as np
import pandas as pd
import soundfile as sf
from datasets import load_dataset
from tqdm import tqdm
import json
from sklearn.model_selection import train_test_split

class AudioStandardizer:
    def __init__(self, target_sr=16000):
        self.target_sr = target_sr

    def process(self, audio_array, original_sr):
        # Ensure mono
        if len(audio_array.shape) > 1:
            audio_array = librosa.to_mono(audio_array)
            
        # Resample
        if original_sr != self.target_sr:
            audio_array = librosa.resample(audio_array, orig_sr=original_sr, target_sr=self.target_sr)
        
        # Normalize amplitude to -1.0 to 1.0 (Peak normalization)
        max_val = np.max(np.abs(audio_array))
        if max_val > 0:
            audio_array = audio_array / max_val
            
        # Trim silence
        audio_array, _ = librosa.effects.trim(audio_array, top_db=30)
        
        return audio_array

def calculate_snr(audio_array):
    """
    Simple SNR estimation: ratio of signal power to noise power.
    """
    # Estimate noise from the quietest 10% of the signal energy
    energy = audio_array**2
    if len(energy) < 100: return 0
    energy_sorted = np.sort(energy)
    noise_floor_energy = np.mean(energy_sorted[:max(1, len(energy)//10)])
    signal_energy = np.mean(energy)
    
    if noise_floor_energy == 0:
        return 50.0 # Arbitrary high SNR
    
    snr = 10 * np.log10(signal_energy / noise_floor_energy)
    return snr

def prepare_dataset(lang_name, repo_id, output_dir, limit=100):
    print(f"Processing {lang_name} from {repo_id} (Limit: {limit})...")
    os.makedirs(os.path.join(output_dir, lang_name), exist_ok=True)
    
    # Try streaming first to save time/space
    try:
        ds = load_dataset(repo_id, split='train', streaming=True, trust_remote_code=True)
    except Exception as e:
        print(f"Streaming not supported for {repo_id}, falling back to download: {e}")
        try:
            ds = load_dataset(repo_id, split='train', trust_remote_code=True)
        except Exception as e2:
            print(f"Fatal error loading {repo_id}: {e2}")
            return None

    standardizer = AudioStandardizer(target_sr=16000)
    metadata = []
    
    count = 0
    # Iterate with tqdm
    pbar = tqdm(total=limit, desc=f"Progress {lang_name}")
    for item in ds:
        if count >= limit:
            break
            
        audio_data = item['audio']
        audio_array = audio_data['array']
        original_sr = audio_data['sampling_rate']
        
        # Standardize
        processed_audio = standardizer.process(audio_array, original_sr)
        
        # Quality Checks
        duration = len(processed_audio) / 16000
        snr = calculate_snr(processed_audio)
        
        # Filtering
        if duration < 0.3: # Skip very short clips
            continue
            
        # Save audio
        filename = f"{lang_name}_{count:06d}.wav"
        filepath = os.path.join(output_dir, lang_name, filename)
        sf.write(filepath, processed_audio, 16000)
        
        metadata.append({
            "id": f"{lang_name}_{count:06d}",
            "language": lang_name,
            "gender": item.get('gender', 'unknown'),
            "duration_sec": round(duration, 3),
            "snr_db": round(snr, 2),
            "original_sr": original_sr,
            "target_sr": 16000,
            "file_path": os.path.join("data/processed", lang_name, filename),
            "label": "human" # Ground truth
        })
        
        count += 1
        pbar.update(1)
        
    pbar.close()
    return metadata

def main():
    datasets_to_process = [
        ("Telugu", "SPRINGLab/IndicTTS_Telugu"),
        ("Hindi", "SPRINGLab/IndicTTS-Hindi"),
        ("Tamil", "SPRINGLab/IndicTTS_Tamil"),
        ("Kannada", "SPRINGLab/IndicTTS_Kannada"),
        ("Malayalam", "SPRINGLab/IndicTTS_Malayalam")
    ]
    
    output_base_dir = "e:/HCL/data/processed"
    reports_dir = "e:/HCL/reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    all_metadata = []
    
    for lang, repo in datasets_to_process:
        meta = prepare_dataset(lang, repo, output_base_dir, limit=100) # 100 per lang for demonstration
        if meta:
            all_metadata.extend(meta)
            
    if not all_metadata:
        print("No data processed. Exiting.")
        return
        
    # Save master metadata
    df = pd.DataFrame(all_metadata)
    master_csv = os.path.join(reports_dir, "human_corpus_metadata.csv")
    df.to_csv(master_csv, index=False)
    
    # Create splits
    try:
        train, test = train_test_split(df, test_size=0.2, stratify=df['language'], random_state=42)
        train.to_csv("e:/HCL/data/train_split.csv", index=False)
        test.to_csv("e:/HCL/data/test_split.csv", index=False)
        print("Created train/test splits.")
    except Exception as e:
        print(f"Error creating splits: {e}")
        # Fallback if stratify fails (e.g. not enough samples per language)
        train, test = train_test_split(df, test_size=0.2, random_state=42)
        train.to_csv("e:/HCL/data/train_split.csv", index=False)
        test.to_csv("e:/HCL/data/test_split.csv", index=False)

    print(f"Total samples processed: {len(all_metadata)}")
    print("Milestone 1 Completed Successfully.")

if __name__ == "__main__":
    main()
