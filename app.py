import streamlit as st
import subprocess
import os
import re
import time

# Configure the page with a minimalist theme
st.set_page_config(
    page_title="YouTube Transcript Fetcher",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a clean and compact UX
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
        font-family: 'Roboto', sans-serif;
    }
    
    .main-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 2rem;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
    }
    
    .main-title {
        font-size: 2rem;
        font-weight: 500;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 300;
    }
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        max-width: 100% !important;
        width: 100% !important;
        background: #ffffff !important;
        border: 1px solid #ecf0f1 !important;
        border-radius: 8px !important;
        color: #2c3e50 !important;
        font-size: 1rem !important;
        padding: 0.7rem 1rem !important;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within {
        border-color: #3498db !important;
    }
    
    .stTextInput > label, .stSelectbox > label {
        color: #2c3e50 !important;
        font-weight: 400 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stButton > button {
        width: 100%;
        padding: 0.8rem;
        background: #3498db;
        border: none;
        border-radius: 8px;
        color: white;
        font-size: 1rem;
        font-weight: 500;
        transition: background 0.3s ease;
    }
    
    .stButton > button:hover {
        background: #2980b9;
    }
    
    .stTextArea > div > div > textarea {
        background: #ffffff !important;
        border: 1px solid #ecf0f1 !important;
        border-radius: 8px !important;
        color: #2c3e50 !important;
    }
    
    .stDownloadButton > button {
        background: #2ecc71;
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        padding: 0.7rem 1.2rem;
        transition: background 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: #27ae60;
    }
    
    .stProgress > div > div > div > div {
        background: #3498db;
    }
    
    .metric-card {
        background: #f9fbfd;
        padding: 0.7rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #ecf0f1;
    }
    
    .metric-value {
        font-size: 1.2rem;
        font-weight: 500;
        color: #2c3e50;
    }
    
    .metric-label {
        color: #7f8c8d;
        font-size: 0.8rem;
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

def clean_vtt(vtt_content):
    no_tags = re.sub(r'<[^>]+>', '', vtt_content)
    lines = no_tags.strip().split('\n')
    clean_lines = [line.strip() for line in lines if line.strip() and not line.startswith('WEBVTT') and '-->' not in line and not line.startswith('Kind:')]
    seen = set()
    unique_lines = [x for x in clean_lines if not (x in seen or seen.add(x))]
    return ' '.join(unique_lines)

def fetch_transcript_text(video_url, lang_code='en'):
    output_filename = f"downloaded_transcript.{lang_code}.vtt"
    try:
        command = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", lang_code,
            "--skip-download",
            "-o", "downloaded_transcript",
            video_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=True)
        if not os.path.exists(output_filename):
            return f"Error: Could not find a transcript for the language '{lang_code}'."
        with open(output_filename, 'r', encoding='utf-8') as f:
            vtt_content = f.read()
        clean_text = clean_vtt(vtt_content)
        return clean_text
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        if "no subtitles available" in error_message.lower():
            return f"Error: This video does not have subtitles available in the language '{lang_code}'."
        return f"Error running yt-dlp: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown("""
<h1 class="main-title">🎬 YouTube Transcript Fetcher</h1>
<p class="subtitle">Extract and download transcripts effortlessly</p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])  # Adjusted to narrower central column

with col2:
    st.markdown('<p style="color: #2c3e50; font-weight: 400; margin-bottom: 0.5rem;">🔗 YouTube Video URL</p>', unsafe_allow_html=True)
    youtube_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        label_visibility="collapsed"
    )
    
    st.markdown('<p style="color: #2c3e50; font-weight: 400; margin-bottom: 0.5rem; margin-top: 1rem;">🌐 Select Language</p>', unsafe_allow_html=True)
    language_options = {
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Russian": "ru",
        "Japanese": "ja",
        "Korean": "ko",
        "Chinese": "zh"
    }
    
    selected_language = st.selectbox(
        "Select Language",
        options=list(language_options.keys()),
        index=0,
        label_visibility="collapsed"
    )
    
    if st.button("Fetch Transcript", use_container_width=True):
        if youtube_url:
            progress_bar = st.progress(0)
            status_text = st.empty()
            for i in range(20):
                progress_bar.progress(i * 5)
                status_text.text(f"Processing... {i * 5}%")
                time.sleep(0.1)
            
            with st.spinner('Fetching transcript...'):
                transcript = fetch_transcript_text(youtube_url, lang_code=language_options[selected_language])
                
                progress_bar.progress(100)
                status_text.text("Done!")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                if transcript.startswith("Error:"):
                    st.error(transcript)
                else:
                    word_count = len(transcript.split())
                    char_count = len(transcript)
                    estimated_read_time = max(1, word_count // 200)
                    
                    st.markdown("### Transcript Stats")
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.markdown('<div class="metric-card"><div class="metric-value">{:,}</div><div class="metric-label">Words</div></div>'.format(word_count), unsafe_allow_html=True)
                    with metric_col2:
                        st.markdown('<div class="metric-card"><div class="metric-value">{:,}</div><div class="metric-label">Characters</div></div>'.format(char_count), unsafe_allow_html=True)
                    with metric_col3:
                        st.markdown('<div class="metric-card"><div class="metric-value">{}</div><div class="metric-label">Est. Read Time</div></div>'.format(f"{estimated_read_time} min"), unsafe_allow_html=True)
                    
                    st.markdown("### Transcript")
                    trans_col1, trans_col2 = st.columns([4, 1])
                    with trans_col1:
                        st.text_area(
                            "Full transcript:",
                            transcript,
                            height=400,
                            label_visibility="collapsed"
                        )
                    with trans_col2:
                        st.download_button(
                            label="Download",
                            data=transcript.encode('utf-8'),
                            file_name="transcript.txt",
                            mime='text/plain',
                            use_container_width=True
                        )
        else:
            st.warning("Please enter a YouTube URL.")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 0.5rem; font-size: 0.9rem;">
    <p>Fast and reliable transcript extraction</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
