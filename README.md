# Mood-Based Spotify Playlist Generator

This Streamlit application analyzes the mood of text input and generates a personalized Spotify playlist based on the detected mood and sentiment.

## Features

- Text mood analysis using Google's Generative AI
- Sentiment analysis using TextBlob
- Automatic Spotify playlist generation
- Mood-based track recommendations
- Sentiment-adjusted playlist customization

## Prerequisites

- Python 3.8 or higher
- Spotify Developer Account
- Google AI API Key

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=your_redirect_uri
   ```

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your actual credentials:
   - Get your Spotify API credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Replace the placeholder values with your actual credentials
   - Never commit your actual `.env` file to version control

3. Make sure your `.env` file is listed in `.gitignore` to prevent accidental commits

## Usage

1. Run the application:
