from spotify_connector import SpotifyConnector
import time
import sys

def check_spotify_setup():
    """Check if Spotify setup is correct and provide instructions if needed."""
    print("\nChecking Spotify setup...")
    print("1. Make sure you have a .env file with these variables:")
    print("   SPOTIFY_CLIENT_ID=your_client_id_here")
    print("   SPOTIFY_CLIENT_SECRET=your_client_secret_here")
    print("   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8501")
    print("\n2. In your Spotify Developer Dashboard:")
    print("   - Go to your application")
    print("   - Click 'Edit Settings'")
    print("   - Under 'Redirect URIs', add: http://127.0.0.1:8501")
    print("   - Save the changes")
    print("\nPress Enter when you've completed these steps...")
    input()

def main():
    try:
        print("Initializing Spotify connector...")
        connector = SpotifyConnector()
        
        # Test moods
        test_moods = ["happy", "sad", "relaxed", "anxious", "excited"]
        
        for mood in test_moods:
            print(f"\n{'='*50}")
            print(f"Testing mood: {mood}")
            print(f"{'='*50}")
            
            # Create a playlist with custom name and description
            print("\nCreating playlist...")
            try:
                playlists = connector.search_playlists_by_genre(
                    mood,
                    playlist_name=f"My {mood.capitalize()} Mix",
                    playlist_description=f"A custom playlist for {mood} moments"
                )
            except Exception as e:
                if "INVALID_CLIENT" in str(e) or "Invalid redirect URI" in str(e):
                    print("\nError: Invalid redirect URI configuration!")
                    print("Please follow these steps:")
                    check_spotify_setup()
                    # Retry after setup
                    playlists = connector.search_playlists_by_genre(
                        mood,
                        playlist_name=f"My {mood.capitalize()} Mix",
                        playlist_description=f"A custom playlist for {mood} moments"
                    )
                else:
                    raise e
            
            if playlists:
                playlist = playlists[0]  # We only create one playlist per mood
                print("\nPlaylist created successfully!")
                print(f"Name: {playlist['name']}")
                print(f"Description: {playlist['description']}")
                print(f"URL: {playlist['url']}")
                print(f"Total tracks: {playlist['total_tracks']}")
                
                # Get tracks from the playlist
                print("\nFetching tracks...")
                tracks = connector.get_playlist_tracks(playlist['id'])
                print(f"Found {len(tracks)} tracks:")
                for i, track in enumerate(tracks[:5], 1):  # Show first 5 tracks
                    print(f"{i}. {track['name']} by {', '.join(track['artists'])}")
                if len(tracks) > 5:
                    print(f"... and {len(tracks) - 5} more tracks")
                
                # Wait a bit before creating next playlist
                time.sleep(2)
            else:
                print(f"Failed to create playlist for {mood} mood")
        
        # Ask user if they want to clean up playlists
        print("\nDo you want to delete all created playlists? (y/n)")
        choice = input().lower()
        if choice == 'y':
            print("\nCleaning up playlists...")
            if connector.cleanup_playlists():
                print("All playlists deleted successfully!")
            else:
                print("Some playlists could not be deleted.")
        else:
            print("\nPlaylists will remain in your Spotify account.")
            print("You can access them through the provided URLs.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "INVALID_CLIENT" in str(e) or "Invalid redirect URI" in str(e):
            check_spotify_setup()
            print("\nPlease run the script again after completing the setup.")
        else:
            print("\nAn unexpected error occurred. Please check your setup and try again.")

if __name__ == "__main__":
    main() 