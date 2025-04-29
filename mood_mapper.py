import json
from typing import List
from pathlib import Path

def get_genres_for_mood(mood: str) -> List[str]:
    """
    Maps a given mood to appropriate music genres based on the JSON mapping.
    
    Args:
        mood (str): The mood to map to music genres
        
    Returns:
        List[str]: A list of music genres that match the given mood
    """
    # Get the path to the JSON file in the same directory
    json_path = Path(__file__).parent / "mood_genres.json"
    
    try:
        # Load the mood-to-genre mapping from JSON
        with open(json_path, 'r') as file:
            mood_to_genres = json.load(file)
        
        # Convert mood to lowercase for case-insensitive matching
        mood = mood.lower()
        
        # Return matching genres or default to pop if mood not found
        return mood_to_genres.get(mood, ["pop"])
    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading mood genres: {e}")
        return ["pop"]

# Test cases
if __name__ == "__main__":
    test_moods = ["happy", "sad", "angry", "unknown"]
    
    print("Testing mood-to-genre mapping:")
    print("-" * 30)
    
    for mood in test_moods:
        genres = get_genres_for_mood(mood)
        print(f"Mood: {mood}")
        print(f"Genres: {', '.join(genres)}")
        print("-" * 30)
