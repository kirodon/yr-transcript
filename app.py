# app.py (Corrected Version)

import streamlit as st
from urllib.parse import urlparse, parse_qs
# CHANGE 1: We now import 'get_transcript' directly
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound, get_transcript

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

def fetch_transcript_text(video_id):
    """
    Fetches the transcript for a given video ID and handles errors.
    Returns the transcript text or an error message string.
    """
    try:
        # CHANGE 2: We now call 'get_transcript' as a direct function
        transcript_list = get_transcript(video_id)
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

youtube_url = st.text_input("Enter YouTube URL:", placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'video_id' not in st.session_state:
    st.session_state.video_id = ""

if st.button("Get Transcript"):
    if youtube_url:
        video_id = get_video_id(youtube_url)
        if video_id:
            with st.spinner('Fetching transcript... Please wait.'):
                st.session_state.video_id = video_id
                st.session_state.transcript = fetch_transcript_text(video_id)
        else:
            st.error("Invalid YouTube URL. Please enter a valid one.")
            st.session_state.transcript = ""
    else:
        st.warning("Please enter a YouTube URL first.")
        st.session_state.transcript = ""

if st.session_state.transcript:
    st.subheader("Transcript:")
    if st.session_state.transcript.startswith("Error:"):
        st.error(st.session_state.transcript)
    else:
        st.text_area("Here is the full transcript:", st.session_state.transcript, height=300)
        st.download_button(
            label="Download Transcript as .txt",
            data=st.session_state.transcript.encode('utf-8'),
            file_name=f"{st.session_state.video_id}_transcript.txt",
            mime='text/plain'
        )
