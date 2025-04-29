import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from typing import List, Dict, Optional
from dotenv import load_dotenv
import time
import webbrowser
import json

class SpotifyConnector:
    def __init__(self):
        """Initialize Spotify connection using environment variables."""
        load_dotenv()
        
        # Get Spotify credentials from environment variables
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8501')
        
        if not client_id or not client_secret:
            raise ValueError(
                "Spotify credentials not found. Please ensure you have set "
                "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file"
            )
        
        try:
            # Initialize Spotify client with client credentials for searching
            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self.sp = spotipy.Spotify(
                auth_manager=auth_manager,
                requests_timeout=10,
                retries=3
            )
            
            # Initialize OAuth for user-specific operations
            self.oauth_manager = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=' '.join([
                    'playlist-modify-public',
                    'playlist-modify-private',
                    'playlist-read-private',
                    'user-read-private',
                    'user-read-email'
                ]),
                show_dialog=True
            )
            
            # Load mood-genre mapping
            with open('mood_genres.json', 'r') as f:
                self.mood_genres = json.load(f)
            
            # Mood-specific keywords for playlist filtering
            self.mood_keywords = {
                'happy': ['happy', 'upbeat', 'joy', 'cheerful', 'positive', 'energetic'],
                'sad': ['sad', 'emotional', 'heartbreak', 'melancholy', 'tears'],
                'relaxed': ['relax', 'calm', 'peaceful', 'chill', 'meditation'],
                'anxious': ['calm', 'peace', 'meditation', 'zen', 'stress relief'],
                'excited': ['excited', 'energetic', 'party', 'dance', 'upbeat'],
                'nostalgic': ['nostalgic', 'retro', 'classic', 'throwback', 'oldies'],
                'romantic': ['romantic', 'love', 'passion', 'intimate', 'sweet'],
                'neutral': ['background', 'study', 'work', 'focus', 'chill']
            }
            
            # Store created playlists for cleanup
            self.created_playlists = []
            
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to Spotify API. Error: {str(e)}\n"
                "Please verify your credentials and internet connection."
            )

    def get_user_token(self):
        """Get user token with proper error handling and retry mechanism."""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                token_info = self.oauth_manager.get_access_token()
                if not token_info:
                    # If no token exists, get a new one
                    auth_url = self.oauth_manager.get_authorize_url()
                    print(f"\nPlease authorize the application by visiting this URL:")
                    print(auth_url)
                    print("\nAfter authorization, you will be redirected to the callback URL.")
                    webbrowser.open(auth_url)
                    
                    # Wait for the user to complete authorization
                    print("\nWaiting for authorization...")
                    time.sleep(10)  # Give user time to complete authorization
                    
                    token_info = self.oauth_manager.get_access_token()
                    if not token_info:
                        raise Exception("Authorization failed or was denied")
                
                return token_info
                
            except Exception as e:
                if "access_denied" in str(e).lower():
                    print("\nAuthorization was denied. Please try again and accept all permissions.")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        raise Exception("Authorization was denied after multiple attempts. Please check your permissions.")
                else:
                    raise e

    def search_playlists_by_genre(
        self, 
        genre: str, 
        limit: int = 5,
        mood: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for playlists by genre with mood-specific filtering.
        
        Args:
            genre: The genre to search for
            limit: Maximum number of playlists to return
            mood: Optional mood to filter playlists by relevance
            
        Returns:
            List of playlist dictionaries with mood relevance scores
        """
        try:
            # Search for playlists with the genre
            results = self.sp.search(
                q=f'genre:"{genre}"',
                type='playlist',
                limit=50  # Get more results to filter
            )
            
            playlists = results['playlists']['items']
            
            # Filter and rank playlists based on mood relevance
            if mood and mood in self.mood_keywords:
                ranked_playlists = []
                keywords = self.mood_keywords[mood]
                
                for playlist in playlists:
                    # Calculate relevance score based on name and description
                    name = playlist['name'].lower()
                    description = playlist.get('description', '').lower()
                    
                    # Count keyword matches
                    score = sum(1 for keyword in keywords if keyword in name or keyword in description)
                    
                    # Add playlist with score
                    ranked_playlists.append({
                        'playlist': playlist,
                        'score': score
                    })
                
                # Sort by relevance score
                ranked_playlists.sort(key=lambda x: x['score'], reverse=True)
                playlists = [item['playlist'] for item in ranked_playlists]
            
            return playlists[:limit]
            
        except Exception as e:
            print(f"Error searching playlists: {str(e)}")
            return []

    def create_mood_playlist(
        self, 
        mood: str,
        playlist_name: Optional[str] = None,
        playlist_description: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create a playlist with songs matching the given mood.
        
        Args:
            mood: The mood to create a playlist for
            playlist_name: Optional custom playlist name
            playlist_description: Optional custom playlist description
            
        Returns:
            Dictionary with playlist details or None if creation failed
        """
        try:
            # Get genres for the mood
            genres = self.mood_genres.get(mood, [])
            if not genres:
                print(f"No genres found for mood: {mood}")
                return None
            
            # Get user token for playlist creation
            token = self.get_user_token()
            if not token:
                return None
            
            # Create playlist
            user_id = self.sp.current_user()['id']
            playlist_name = playlist_name or f"{mood.capitalize()} Mood Playlist"
            playlist_description = playlist_description or f"Songs to match your {mood} mood"
            
            playlist = self.sp.user_playlist_create(
                user_id,
                playlist_name,
                public=True,
                description=playlist_description
            )
            
            # Search for playlists in each genre
            all_tracks = set()
            for genre in genres:
                playlists = self.search_playlists_by_genre(genre, mood=mood)
                
                for playlist in playlists:
                    tracks = self.get_playlist_tracks(playlist['id'])
                    all_tracks.update(tracks)
            
            # Add tracks to the playlist
            if all_tracks:
                track_uris = [track['uri'] for track in all_tracks]
                self.sp.playlist_add_items(playlist['id'], track_uris)
            
            # Store playlist for cleanup
            self.created_playlists.append(playlist['id'])
            
            return playlist
            
        except Exception as e:
            print(f"Error creating mood playlist: {str(e)}")
            return None

    def get_playlist_tracks(self, playlist_id: str, limit: int = 10) -> List[Dict]:
        """
        Get tracks from a playlist with mood relevance filtering.
        
        Args:
            playlist_id: The Spotify playlist ID
            limit: Maximum number of tracks to return
            
        Returns:
            List of track dictionaries
        """
        try:
            results = self.sp.playlist_tracks(playlist_id)
            tracks = results['items']
            
            # Get more tracks if available
            while results['next'] and len(tracks) < limit:
                results = self.sp.next(results)
                tracks.extend(results['items'])
            
            return tracks[:limit]
            
        except Exception as e:
            print(f"Error getting playlist tracks: {str(e)}")
            return []

    def delete_playlist(self, playlist_id: str) -> bool:
        """
        Delete a playlist by its ID.
        
        Args:
            playlist_id (str): The ID of the playlist to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Get user token
            token_info = self.oauth_manager.get_access_token()
            if not token_info:
                raise Exception("Failed to get access token")
            
            # Create Spotify client with user token
            sp_user = spotipy.Spotify(auth=token_info['access_token'])
            
            # Unfollow (delete) the playlist
            sp_user.current_user_unfollow_playlist(playlist_id)
            
            # Remove from created_playlists if it exists
            if playlist_id in self.created_playlists:
                self.created_playlists.remove(playlist_id)
            
            return True
            
        except Exception as e:
            print(f"Error deleting playlist: {e}")
            return False

    def cleanup_playlists(self) -> bool:
        """
        Delete all playlists created during this session.
        
        Returns:
            bool: True if all playlists were deleted successfully, False otherwise
        """
        success = True
        for playlist_id in self.created_playlists[:]:  # Create a copy of the list
            if not self.delete_playlist(playlist_id):
                success = False
        
        return success

    def get_track_preview(self, track_id: str) -> Optional[str]:
        """
        Get the preview URL for a specific track.
        
        Args:
            track_id (str): Spotify track ID
            
        Returns:
            Optional[str]: Preview URL if available, None otherwise
        """
        try:
            track = self.sp.track(track_id)
            return track.get('preview_url')
        except Exception as e:
            print(f"Error getting track preview: {e}")
            return None

# Test the Spotify connector
if __name__ == "__main__":
    try:
        print("Initializing Spotify connector...")
        connector = SpotifyConnector()
        
        # Test with different moods
        test_moods = ["happy", "sad", "relaxed", "anxious", "excited"]
        
        for mood in test_moods:
            print(f"\nTesting playlist search for '{mood}' mood:")
            playlists = connector.search_playlists_by_genre(mood, limit=1)
            
            if playlists:
                for playlist in playlists:
                    print(f"\nPlaylist: {playlist['name']}")
                    print(f"Description: {playlist['description']}")
                    if 'is_default' in playlist:
                        print("Default Playlist Songs:")
                        for song in playlist['songs']:
                            print(f"- {song}")
                    else:
                        print(f"Tracks: {playlist['total_tracks']}")
                        print(f"URL: {playlist['url']}")
                        
                        # Test getting tracks
                        print("\nFetching tracks...")
                        tracks = connector.get_playlist_tracks(playlist['id'], limit=3)
                        for track in tracks:
                            print(f"- {track['name']} by {', '.join(track['artists'])}")
            else:
                print("No playlists found!")
    
    except Exception as e:
        print(f"Error in test: {e}") 