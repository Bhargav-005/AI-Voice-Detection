# Milestone 1: Multilingual Human Speech Dataset Preparation

## Objective
Establish a high-quality, multilingual human speech foundation as a ground truth for AI-generated voice detection.

## Dataset Highlights
We utilize the **SPRINGLab IndicTTS** datasets (Studio Recorded Human Speech) for five major Indian languages:
- Hindi
- Telugu
- Tamil
- Kannada
- Malayalam

## Audio Standardization Pipeline
Our pipeline ensures uniform processing to eliminate artifacts:
1. **Resampling**: All audio resampled to **16 kHz**.
2. **Format**: Converted to single-channel **WAV**.
3. **Normalization**: Peak amplitude normalization to -1.0 to 1.0.
4. **Silence Trimming**: Removed leading/trailing silence using Librosa (30dB threshold).
5. **Quality Filtering**: Excluded clips shorter than 0.5s and verified SNR.

## Metadata & Validation
Each sample is validated for:
- **Sampling Rate**: Verified at 16kHz.
- **SNR (Signal-to-Noise Ratio)**: Estimated to ensure clarity.
- **Duration Distribution**: Tracked for balanced training.

## Results
- **Processed Corpus**: Located in `data/processed/`.
- **Master Metadata**: `reports/human_corpus_metadata.csv`.
- **Dataset Splits**:
  - `data/train_split.csv` (80%)
  - `data/test_split.csv` (20%)

## How to Reproduce
1. Install dependencies: `pip install datasets librosa soundfile tqdm pandas scikit-learn`
2. Run the preparation script: `python src/data_preparation.py`

## Anti-Hard-Coding Compliance
- All processing is data-driven.
- No language-specific hard-coded thresholds were used; the system learns natural variations from the standardized corpus.
