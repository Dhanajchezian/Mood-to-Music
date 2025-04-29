import streamlit as st

# Set page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="Mood-to-Music",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

from text_mood_detector import detect_mood_from_text
from mood_mapper import get_genres_for_mood
from spotify_connector import SpotifyConnector
import json
import time
import webbrowser
import os
from dotenv import load_dotenv
import google.generativeai as genai
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from textblob import TextBlob

# Load environment variables
load_dotenv()

# Configure Google AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    st.error("Please set your GOOGLE_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model with error handling
try:
    models = genai.list_models()
    # Prefer gemini-1.5-flash if available
    model = None
    preferred_model_name = "models/gemini-1.5-flash"
    for m in models:
        if m.name == preferred_model_name and hasattr(m, "supported_generation_methods") and "generateContent" in m.supported_generation_methods:
            model = genai.GenerativeModel(m.name)
            break
    if not model:
        # Fallback: use any model that supports generateContent
        for m in models:
            if hasattr(m, "supported_generation_methods") and "generateContent" in m.supported_generation_methods:
                model = genai.GenerativeModel(m.name)
                break
    if not model:
        st.error("No suitable model found that supports generateContent. Please check your API key and permissions.")
        st.stop()
except Exception as e:
    st.error(f"Error initializing Google AI model: {str(e)}")
    st.stop()

# Configure Spotify
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8501"

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    st.error("Please set your SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in the .env file")
    st.stop()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope='playlist-modify-public'
))

# Initialize Spotify connector with default songs
@st.cache_resource
def get_spotify_connector():
    connector = SpotifyConnector()
    # Add default songs if not present
    if not hasattr(connector, 'default_songs'):
        connector.default_songs = {
            'happy': ['Happy - Pharrell Williams', 'Can\'t Stop the Feeling - Justin Timberlake'],
            'sad': ['Someone Like You - Adele', 'All I Want - Kodaline'],
            'angry': ['In the End - Linkin Park', 'Numb - Linkin Park'],
            'calm': ['Weightless - Marconi Union', 'Clair de Lune - Debussy'],
            'energetic': ['Uptown Funk - Mark Ronson', 'Can\'t Hold Us - Macklemore'],
            'romantic': ['Perfect - Ed Sheeran', 'All of Me - John Legend'],
            'anxious': ['Breathe Me - Sia', 'Fix You - Coldplay']
        }
    return connector

# Load mood-genre mapping
@st.cache_data
def load_mood_genres():
    with open('mood_genres.json', 'r') as f:
        return json.load(f)

def analyze_mood(text):
    """Analyze the mood of the input text using Google's Generative AI."""
    try:
        prompt = f"Analyze the mood of this text and return a single word describing the primary emotion: {text}"
        response = model.generate_content(prompt)
        if not response.text:
            return "neutral"
        return response.text.strip().lower()
    except Exception as e:
        st.error(f"Error analyzing mood: {str(e)}")
        return "neutral"

def get_sentiment_score(text):
    """Get the sentiment score of the text using TextBlob."""
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def create_playlist(mood, sentiment_score):
    """Create a Spotify playlist based on mood and sentiment."""
    # Map mood to Spotify search query
    mood_to_query = {
        'happy': 'upbeat pop',
        'sad': 'melancholic indie',
        'angry': 'aggressive rock',
        'calm': 'ambient relaxation',
        'energetic': 'dance electronic',
        'romantic': 'love songs',
        'anxious': 'soothing meditation'
    }
    
    query = mood_to_query.get(mood, 'mood music')
    
    # Adjust query based on sentiment score
    if sentiment_score > 0.5:
        query += ' positive'
    elif sentiment_score < -0.5:
        query += ' sad'
    
    # Search for tracks
    results = sp.search(q=query, type='track', limit=20)
    track_uris = [track['uri'] for track in results['tracks']['items']]
    
    # Create playlist
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(
        user_id,
        f'Mood Playlist: {mood.capitalize()}',
        public=True,
        description=f'Generated based on {mood} mood and sentiment score: {sentiment_score:.2f}'
    )
    
    # Add tracks to playlist
    sp.playlist_add_items(playlist['id'], track_uris)
    
    return playlist['external_urls']['spotify']

def main():
    # Sidebar
    with st.sidebar:
        st.title("🎵 Mood-to-Music")
        st.markdown("""
        ### How it works:
        1. Share how you're feeling
        2. We'll detect your mood
        3. Get personalized music recommendations
        4. Create a Spotify playlist just for you!
        """)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app uses AI to understand your mood and suggest the perfect music.
        Just type how you're feeling, and we'll do the rest!
        """)

    # Main content
    st.title("🎵 How are you feeling today?")
    
    # Text input for mood
    user_input = st.text_area(
        "Share your thoughts...",
        placeholder="I'm feeling happy because...\nI'm feeling sad because...\nI'm feeling excited about...",
        height=150
    )
    
    if user_input:
        with st.spinner("Analyzing your mood..."):
            try:
                # Analyze mood
                mood = analyze_mood(user_input)
                sentiment_score = get_sentiment_score(user_input)
                
                # Display results
                st.success(f"🎭 We detected that you're feeling **{mood.capitalize()}**")
                
                # Create a playlist button
                if st.button("🎧 Create a Spotify Playlist", type="primary"):
                    try:
                        with st.spinner("Creating your playlist..."):
                            # Generate playlist
                            playlist_url = create_playlist(mood, sentiment_score)
                            
                            if playlist_url:
                                st.success("🎉 Playlist created successfully!")
                                
                                # Display playlist info
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    if playlist_url:
                                        st.image(f"https://i.scdn.co/image/{playlist_url.split('/')[-1]}", width=200)
                                
                                with col2:
                                    st.markdown(f"""
                                    ### {mood.capitalize()} Playlist
                                    Sentiment Score: {sentiment_score:.2f}
                                    
                                    [🎵 Listen on Spotify]({playlist_url})
                                    """)
                                    # Replace button with a link that opens in a new tab
                                    st.markdown(f'<a href="{playlist_url}" target="_blank">Open in Spotify to listen</a>', unsafe_allow_html=True)
                            else:
                                st.error("Could not create playlist. Please try again.")
                    
                    except Exception as e:
                        st.error("An error occurred while creating your playlist.")
                        st.error(str(e))
                
                # Display genre suggestions
                st.subheader("🎵 Suggested Genres")
                genres = get_genres_for_mood(mood)
                for genre in genres:
                    st.markdown(f"- **{genre.capitalize()}**")
                
                # Add a separator
                st.markdown("---")
                
                # Display mood-specific songs
                st.subheader("🎧 Popular Songs for Your Mood")
                try:
                    spotify = get_spotify_connector()
                    songs = spotify.default_songs.get(mood, [])
                    
                    if songs:
                        # Split songs into English and Tamil
                        english_songs = [s for s in songs if " - " in s and not any(t in s for t in ["A.R. Rahman", "Harris Jayaraj", "Yuvan Shankar Raja"])]
                        tamil_songs = [s for s in songs if any(t in s for t in ["A.R. Rahman", "Harris Jayaraj", "Yuvan Shankar Raja"])]
                        
                        # Display English songs
                        if english_songs:
                            st.markdown("#### English Songs")
                            for song in english_songs[:10]:  # Show top 10
                                st.markdown(f"- {song}")
                        
                        # Display Tamil songs
                        if tamil_songs:
                            st.markdown("#### Tamil Songs")
                            for song in tamil_songs[:10]:  # Show top 10
                                st.markdown(f"- {song}")
                    else:
                        st.info("No songs available for this mood yet.")
                
                except Exception as e:
                    st.error("Could not load song recommendations.")
                    st.error(str(e))
            
            except Exception as e:
                st.error(f"Error analyzing mood: {str(e)}")
                st.error("Please try again with different text.")

    # Add delete playlist button if a playlist exists
    if 'current_playlist_id' in st.session_state:
        st.markdown("---")
        st.subheader("🎵 Playlist Management")
        if st.button("🗑️ Delete Current Playlist", type="secondary"):
            try:
                with st.spinner("Deleting playlist..."):
                    spotify = get_spotify_connector()
                    if spotify.delete_playlist(st.session_state['current_playlist_id']):
                        st.success("✅ Playlist deleted successfully!")
                        del st.session_state['current_playlist_id']
                    else:
                        st.error("❌ Failed to delete playlist. Please try again.")
            except Exception as e:
                st.error("An error occurred while deleting the playlist.")
                st.error(str(e))

if __name__ == "__main__":
    # Open browser automatically
    if not os.environ.get("STREAMLIT_BROWSER_OPENED"):
        os.environ["STREAMLIT_BROWSER_OPENED"] = "1"
        webbrowser.open("http://localhost:8501")
    
    main() 