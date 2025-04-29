import os
import google.generativeai as genai
import time
from dotenv import load_dotenv
from collections import Counter
import re

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Keyword-based mood detection with improved weights and exclusions
MOOD_KEYWORDS = {
    'happy': {
        'keywords': ['amazing', 'wonderful', 'thrilled', 'fantastic', 'overjoyed', 'happy', 'joy', 'delight', 'great', 'awesome', 'smiling', 'laughing', 'cheerful'],
        'weight': 1.2,  # Reduced weight
        'exclude': ['worried', 'nervous', 'anxious', 'sad', 'depressed', 'miserable', 'excited', 'content', 'good', 'pleasant']  # Added more exclusions
    },
    'sad': {
        'keywords': ['crying', 'down', 'disappointing', 'upset', 'blue', 'sad', 'unhappy', 'grieving', 'depressed', 'miserable', 'heartbroken', 'tears', 'lonely', 'hurt', 'pain'],
        'weight': 1.4,
        'exclude': ['happy', 'excited', 'joyful', 'cheerful', 'anxious']
    },
    'anxious': {
        'keywords': ['anxious', 'nervous', 'worried', 'terrified', 'afraid', 'scared', 'fear', 'stressed', 'tense', 'panicked', 'overwhelmed', 'uneasy', 'apprehensive', 'frightened', 'distressed', 'terrible'],
        'weight': 1.6,
        'exclude': ['happy', 'excited', 'relaxed', 'calm', 'peaceful']
    },
    'excited': {
        'keywords': ['excited', 'pumped', 'eager', 'enthusiastic', 'can\'t wait', 'looking forward', 'thrilled', 'anticipating', 'waiting for', 'energetic', 'pumped up', 'hyped', 'stoked', 'psyched'],
        'weight': 1.5,  # Increased weight
        'exclude': ['worried', 'nervous', 'anxious', 'sad', 'depressed', 'happy', 'content', 'calm']
    },
    'relaxed': {
        'keywords': ['relaxed', 'calm', 'peaceful', 'content', 'at ease', 'chill', 'laid back', 'serene', 'tranquil', 'unwind', 'mellow', 'easygoing', 'composed', 'collected', 'restful', 'pleasant', 'smoothly', 'good'],
        'weight': 1.5,  # Increased weight
        'exclude': ['excited', 'worried', 'nervous', 'anxious', 'stressed', 'happy', 'thrilled']
    },
    'nostalgic': {
        'keywords': ['nostalgic', 'memories', 'remember', 'miss', 'good old days', 'back then', 'childhood', 'past', 'reminiscing', 'throwback', 'reminiscent', 'reminiscence', 'recollection', 'memory', 'fondly'],
        'weight': 1.4,  # Increased weight
        'exclude': ['present', 'future', 'now', 'current', 'happy', 'excited']
    },
    'romantic': {
        'keywords': ['romantic', 'love', 'loving', 'affectionate', 'passionate', 'smitten', 'enchanted', 'heart', 'sweet', 'dear', 'adore', 'cherish', 'devoted', 'fond', 'infatuated'],
        'weight': 1.4,
        'exclude': ['hate', 'dislike', 'angry', 'upset', 'happy']
    },
    'neutral': {
        'keywords': ['neutral', 'average', 'typical', 'usual', 'neither', 'normal', 'regular', 'ordinary', 'standard', 'moderate', 'balanced', 'even', 'steady', 'stable', 'nothing special', 'business as usual'],
        'weight': 1.0,  # Increased weight
        'exclude': ['happy', 'sad', 'excited', 'anxious', 'relaxed']
    }
}

def keyword_based_detection(text):
    """
    Detect mood using keyword matching with improved confidence scoring.
    Returns (mood, confidence) tuple.
    """
    if not text or text.isspace():
        return 'neutral', 1.0

    # Clean and normalize text
    text = text.lower()
    words = re.findall(r'\w+', text)
    phrases = [text[i:i+3] for i in range(len(text)-2)]  # Look for 3-word phrases
    
    # Count keyword matches for each mood
    mood_scores = {}
    for mood, data in MOOD_KEYWORDS.items():
        # Count positive matches (both words and phrases)
        word_matches = sum(1 for word in words if word in data['keywords'])
        phrase_matches = sum(1 for phrase in phrases if any(keyword in phrase for keyword in data['keywords']))
        matches = word_matches + phrase_matches
        
        # Subtract points for excluded words (increased penalty)
        excluded_matches = sum(3 for word in words if word in data.get('exclude', []))
        
        # Calculate final score with improved weighting
        base_score = matches * 2.5 - excluded_matches
        
        # Apply mood-specific adjustments
        if mood == 'neutral' and base_score <= 0:
            base_score = 1  # Bias towards neutral for ambiguous cases
        
        mood_scores[mood] = base_score * data['weight']
    
    # Get the mood with highest score
    if not mood_scores or all(score <= 0 for score in mood_scores.values()):
        return 'neutral', 1.0
    
    # Special handling for neutral mood
    if any(score > 0 for score in mood_scores.values()):
        max_score = max(mood_scores.values())
        if max_score < 1.5:  # If all scores are low, prefer neutral
            return 'neutral', 1.0
    
    max_mood = max(mood_scores.items(), key=lambda x: x[1])[0]
    max_score = mood_scores[max_mood]
    
    # Calculate confidence (normalized score)
    total_score = sum(abs(score) for score in mood_scores.values())
    confidence = abs(max_score) / total_score if total_score > 0 else 0.0
    
    # Additional confidence check for neutral
    if confidence < 0.3 and not any(score > 2 for score in mood_scores.values()):
        return 'neutral', 1.0
    
    return max_mood, confidence

def ml_based_detection(text):
    """
    Detect mood using the Gemini model with improved prompt.
    """
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                                    generation_config={
                                        "temperature": 0.1,
                                        "top_p": 0.1,
                                        "top_k": 1
                                    })

        prompt = f"""
        Analyze the following text and determine the primary mood expressed.
        Consider the context and emotional tone carefully.
        Choose EXACTLY ONE mood from: happy, relaxed, neutral, sad, anxious, excited, nostalgic, romantic.
        Only respond with the mood word, nothing else.
        
        Text: {text}
        """

        response = model.generate_content(prompt)
        detected_mood = response.text.strip().lower()
        
        # Validate the detected mood
        valid_moods = set(MOOD_KEYWORDS.keys())
        if detected_mood not in valid_moods:
            return 'neutral'
        
        return detected_mood

    except Exception as e:
        print(f"Error in ML mood detection: {str(e)}")
        return 'neutral'

def detect_mood_from_text(text):
    """
    Hybrid mood detection that combines keyword-based and ML-based approaches
    with improved confidence thresholds and fallback logic.
    """
    # First try keyword-based detection
    mood, confidence = keyword_based_detection(text)
    
    # If confidence is low or we hit certain edge cases, use ML
    if confidence < 0.4:  # Increased threshold for using ML
        try:
            ml_mood = ml_based_detection(text)
            # Only use ML result if it's different and has high confidence
            if ml_mood != mood and confidence < 0.3:
                return ml_mood
        except Exception as e:
            print(f"ML detection failed, using keyword result: {mood}")
    
    return mood

# Test cases
if __name__ == "__main__":
    test_cases = [
        "I'm feeling amazing today!",
        "Just an average day",
        "I'm worried about the exam tomorrow",
        "Remembering the good old days",
        "I'm in a romantic mood this evening",
        "Feeling calm and peaceful",
        "I'm so excited for the concert!",
        "This makes me really anxious",
        "I'm feeling a bit down today"
    ]
    
    print("Mood Detection Results:")
    print("-" * 50)
    for text in test_cases:
        mood = detect_mood_from_text(text)
        print(f"Text: {text}")
        print(f"Detected Mood: {mood}")
        print("-" * 50) 