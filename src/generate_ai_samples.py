"""
Generate AI/Synthetic speech samples using gTTS (Google Text-to-Speech)
for testing the AI voice detection system.
"""
import os
from gtts import gTTS
from tqdm import tqdm

def generate_synthetic_samples():
    """Generate AI speech samples in multiple languages"""
    
    # Sample texts in different Indian languages
    samples = [
        # Hindi
        ("hi", "नमस्ते, मैं एक कृत्रिम बुद्धिमत्ता आवाज़ हूं।", "hindi_ai_001"),
        ("hi", "यह एक परीक्षण संदेश है।", "hindi_ai_002"),
        ("hi", "कृपया ध्यान से सुनें।", "hindi_ai_003"),
        
        # Tamil
        ("ta", "வணக்கம், நான் ஒரு செயற்கை நுண்ணறிவு குரல்.", "tamil_ai_001"),
        ("ta", "இது ஒரு சோதனை செய்தி.", "tamil_ai_002"),
        
        # Telugu
        ("te", "నమస్కారం, నేను కృత్రిమ మేధస్సు వాయిస్.", "telugu_ai_001"),
        ("te", "ఇది ఒక పరీక్ష సందేశం.", "telugu_ai_002"),
        
        # Kannada  
        ("kn", "ನಮಸ್ಕಾರ, ನಾನು ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಧ್ವನಿ.", "kannada_ai_001"),
        
        # Malayalam
        ("ml", "നമസ്കാരം, ഞാൻ ഒരു കൃത്രിമ ബുദ്ധി ശബ്ദം.", "malayalam_ai_001"),
        
        # English (for comparison)
        ("en", "Hello, I am an artificial intelligence voice.", "english_ai_001"),
        ("en", "This is a test message for voice detection.", "english_ai_002"),
        ("en", "Please listen carefully to this synthetic speech.", "english_ai_003"),
    ]
    
    output_dir = "e:/HCL/data/synthetic/gtts"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating AI speech samples using gTTS...")
    for lang_code, text, filename in tqdm(samples, desc="Generating"):
        try:
            tts = gTTS(text=text, lang=lang_code, slow=False)
            filepath = os.path.join(output_dir, f"{filename}.mp3")
            tts.save(filepath)
        except Exception as e:
            print(f"Error generating {filename}: {e}")
    
    print(f"Generated {len(samples)} AI speech samples in {output_dir}")
    return output_dir

if __name__ == "__main__":
    # Check if gtts is installed
    try:
        import gtts
    except ImportError:
        print("Installing gTTS...")
        os.system("pip install gtts")
        
    generate_synthetic_samples()
