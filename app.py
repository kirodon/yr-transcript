# app.py

import streamlit as st
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def get_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    if not url:
        return None
    
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p.get('v', [None])[0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

def get_transcript(video_id):
    """
    Fetches the transcript for a given video ID and handles errors.
    Returns the transcript text or an error message string.
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([item['text'] for item in transcript_list])
    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "Error: No transcript could be found for this video. It might be a music video, too new, or in a language without auto-captions."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Streamlit Web App Interface ---

st.set_page_config(page_title="YouTube Transcript Fetcher", layout="centered")

st.title("YouTube Video Transcript Fetcher")
st.write("Paste a YouTube video URL below to get its full transcript.")

# Input field for the YouTube URL
youtube_url = st.text_input("Enter YouTube URL:", placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Session state to hold the transcript
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'video_id' not in st.session_state:
    st.session_state.video_id = ""

# Button to fetch the transcript
if st.button("Get Transcript"):
    if youtube_url:
        video_id = get_video_id(youtube_url)
        if video_id:
            with st.spinner('Fetching transcript... Please wait.'):
                st.session_state.video_id = video_id
                st.session_state.transcript = get_transcript(video_id)
        else:
            st.error("Invalid YouTube URL. Please enter a valid one.")
            st.session_state.transcript = "" # Clear previous transcript on error
    else:
        st.warning("Please enter a YouTube URL first.")
        st.session_state.transcript = "" # Clear transcript if input is empty

# Display the transcript in a text area if it exists
if st.session_state.transcript:
    st.subheader("Transcript:")
    st.text_area("Here is the full transcript:", st.session_state.transcript, height=300)
    
    # Add a download button
    st.download_button(
        label="Download Transcript as .txt",
        data=st.session_state.transcript.encode('utf-8'),
        file_name=f"{st.session_state.video_id}_transcript.txt",
        mime='text/plain'
    )