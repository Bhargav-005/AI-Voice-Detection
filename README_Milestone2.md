# Milestone 2: Feature Engineering & Human Speech Profiling

## Objective
Deeply characterize human speech using robust, language-agnostic audio features to establish a "Human Fingerprint" reference.

## Engineered Features
Our pipeline (`src/feature_engineering.py`) extracts a comprehensive set of features:

### 1. Spectral Features (Timbre & Clarity)
- **MFCCs (13 coefficients)**: Captures the shape of the vocal tract.
- **Spectral Centroid**: Indicates the "brightness" of the sound.
- **Spectral Bandwidth**: Measure of frequency spread.
- **Spectral Flatness**: Distinguishes between tone-like and noise-like sounds.
- **Spectral Rolloff**: Captures the frequency below which 85% of energy lies.

### 2. Prosodic & Micro-Variation Features (Natural Imperfections)
- **Fundamental Frequency (F0)**: Characterizes voice pitch.
- **Jitter (Frequency Variation)**: Measures micro-fluctuations in pitch period.
- **Shimmer (Amplitude Variation)**: Measures micro-fluctuations in amplitude peaks.
*These features are critical as synthetic voices often lack the natural jitter/shimmer found in human speech.*

### 3. Temporal & Rhythm Features (Flow)
- **Zero-Crossing Rate (ZCR)**: Rate of sign-changes in the signal.
- **Energy Entropy**: Captures the distribution of energy over time, modeling natural pauses and emphasis.

## Human Speech Statistical Profile
We computed a global statistical profile across all five Indian languages:
- **Location**: `reports/human_feature_profile.json`
- **Metrics**: Includes Mean, Std, Min/Max, and Interquartile ranges for every feature.

## Synthetic Readiness Framework
The system is designed to be "Synthetic Ready":
- **Unified Pipeline**: The same `FeatureExtractor` class will be used for both human and synthetic voices.
- **Anomaly Scoring Prototype**: We've established a Z-score based deviation detection method that can identify "non-human" speech behavior by measuring distance from the established human profile.

## Anti-Hard-Coding Compliance
- **No manual thresholds**: All "normality" limits are derived statistically from the human corpus.
- **Language Agnostic**: Features are normalized using corpus-level statistics, ensuring fairness across linguistic variations.
