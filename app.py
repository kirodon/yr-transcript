# app.py - Correct code for youtube-transcript-api v1.2.2
import streamlit as st
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    if not url: 
        return None
    
    query = urlparse(url)
    
    if query.hostname == 'youtu.be': 
        return query.path[1:]
    
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch': 
            return parse_qs(query.query).get('v', [None])[0]
        if query.path[:7] == '/embed/': 
            return query.path.split('/')[2]
        if query.path[:3] == '/v/': 
            return query.path.split('/')[2]
    
    return None

def fetch_transcript_text(video_id):
    """Fetches the transcript using the NEW v1.2.2 API."""
    try:
        # Create an instance of the API (NEW in v1.2.2)
        ytt_api = YouTubeTranscriptApi()
        
        # Use .fetch() method instead of .get_transcript()
        transcript = ytt_api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
        
        # Convert to raw data and extract text
        transcript_data = transcript.to_raw_data()
        return "\n".join([item['text'] for item in transcript_data])
        
    except Exception as e:
        # Try alternative approach if the first one fails
        try:
            ytt_api = YouTubeTranscriptApi()
            # Use .list() method to get available transcripts
            transcript_list = ytt_api.list(video_id)
            
            # Find an English transcript
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
            
            # Fetch the transcript
            fetched_transcript = transcript.fetch()
            
            # Convert to text
            transcript_data = fetched_transcript.to_raw_data()
            return "\n".join([item['text'] for item in transcript_data])
            
        except Exception as e2:
            return f"Error: Could not fetch transcript. {str(e)}. Alternative error: {str(e2)}"

# --- Streamlit Web App Interface ---
st.set_page_config(page_title="YouTube Transcript Fetcher", layout="centered")
st.title("YouTube Video Transcript Fetcher")
st.write("Paste a YouTube video URL below to get its full transcript.")

youtube_url = st.text_input("Enter YouTube URL:", placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if st.button("Get Transcript"):
    if youtube_url:
        video_id = get_video_id(youtube_url)
        if video_id:
            with st.spinner('Fetching transcript...'):
                transcript = fetch_transcript_text(video_id)
                if transcript.startswith("Error:"):
                    st.error(transcript)
                else:
                    st.subheader("Transcript:")
                    st.text_area("Full transcript:", transcript, height=300)
                    st.download_button(
                        label="Download Transcript as .txt",
                        data=transcript.encode('utf-8'),
                        file_name=f"{video_id}_transcript.txt",
                        mime='text/plain'
                    )
        else:
            st.error("Invalid YouTube URL. Please enter a valid one.")
    else:
        st.warning("Please enter a YouTube URL first.")

# Debug section
st.sidebar.header("Debug Info")
if st.sidebar.checkbox("Show API Version Info"):
    st.sidebar.write("Using youtube-transcript-api v1.2.2")
    st.sidebar.write("New API methods:")
    st.sidebar.write("- Create instance: `ytt_api = YouTubeTranscriptApi()`")
    st.sidebar.write("- Fetch transcript: `ytt_api.fetch(video_id)`")
    st.sidebar.write("- List transcripts: `ytt_api.list(video_id)`")
