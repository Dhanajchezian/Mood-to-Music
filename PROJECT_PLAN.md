# Project Plan: Mood-Based Music Recommendation System

## 1. Project Overview
- **Goal**: Create a system that recommends music based on user's mood
- **Components**: Mood detection, Spotify integration, playlist management
- **Status**: In Progress

## 2. Current Progress

### 2.1 Mood Detection System
- ✅ Implemented hybrid mood detection (keyword + ML)
- ✅ Enhanced keyword lists and weights
- ✅ Added confidence scoring
- ✅ Improved edge case handling
- ⚠️ Remaining Issues:
  - Some confusion between 'happy' and 'excited' moods
  - Over-detection of 'relaxed' mood
  - Under-detection of 'nostalgic' mood
  - Mixed emotions handling needs improvement

### 2.2 Spotify Integration
- ✅ Basic Spotify API connection
- ✅ Playlist recommendation system
- ✅ Genre-based mood mapping
- ⚠️ Needs improvement:
  - Better playlist selection for edge cases
  - More diverse genre recommendations
  - Improved error handling

### 2.3 Testing
- ✅ Unit tests for mood detection
- ✅ Test cases for various moods
- ⚠️ Current Test Status:
  - 6/10 tests passing
  - 4 tests failing (happy, neutral, nostalgic, edge cases)

## 3. Next Steps

### 3.1 Immediate Tasks
1. Fix mood detection issues:
   - Adjust weights for 'happy' vs 'excited'
   - Improve 'relaxed' mood detection
   - Enhance 'nostalgic' mood detection
   - Better handling of mixed emotions

2. Improve Spotify integration:
   - Update playlist selection logic
   - Add more genre categories
   - Implement better error handling

## 4. Technical Details

### 4.1 Current Implementation
- Using Gemini 2.0 Flash for ML-based detection
- Hybrid approach combining keyword and ML detection
- Confidence-based fallback system
- Enhanced keyword lists with weights and exclusions

### 4.2 Dependencies
- google-generativeai>=0.3.0
- spotipy>=2.23.0
- python-dotenv>=1.0.0
- TextBlob>=0.17.1

## 5. Timeline
- Current Phase: Testing and Refinement
- Next Phase: Production Deployment
- Target Completion: TBD

## 6. Notes
- Need to address remaining test failures
- Consider adding more sophisticated ML models
- Plan for scaling and performance optimization

## File Structure
```
project/
├── mood_genres.json          # Mood-to-genre mapping
├── mood_mapper.py           # Genre mapping functions
├── text_mood_detector.py    # Text-based mood detection
├── spotify_connector.py     # Spotify API integration
├── test_spotify.py          # Spotify integration tests
├── app.py                   # Streamlit main application
├── requirements.txt         # Project dependencies
└── venv/                    # Virtual environment
```

## Environment Variables
```
GOOGLE_API_KEY=your_google_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

def detect_mood_from_text(text):
    # Try keyword detection first
    mood, confidence = keyword_based_detection(text)
    
    # If confidence is low, use ML
    if confidence < 0.3:
        try:
            return ml_based_detection(text)
        except Exception:
            return mood  # Fallback to keyword result
    
    return mood 