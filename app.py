import streamlit as st
import subprocess
import os
import re
import time
import shutil
import glob

# Configure the page with a minimalist theme
st.set_page_config(
    page_title="YouTube Transcript Fetcher",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
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
    
    .main-title {
        font-size: 1.8rem;
        font-weight: 500;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.8rem;
    }
    
    .subtitle {
        font-size: 0.85rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 300;
    }
    
    .stTextInput > div > div > input {
        background: #ffffff !important;
        border: 1px solid #ecf0f1 !important;
        border-radius: 6px !important;
        color: #2c3e50 !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 0.9rem !important;
    }

    /* --- THIS IS THE CORRECTED SECTION FOR THE DROPDOWN --- */
    /* This styles the outer box of the dropdown */
    .stSelectbox div[data-baseweb="select"] {
        background: #ffffff !important;
        border: 1px solid #ecf0f1 !important;
        border-radius: 6px !important;
        font-size: 0.95rem !important;
        padding: 0.1rem 0.4rem !important; /* Adjusted padding */
    }
    /* This specifically targets the VISIBLE TEXT inside the dropdown */
    .stSelectbox div[data-baseweb="select"] > div > div {
        color: #2c3e50 !important;
        background-color: transparent !important;
    }
    
    .stButton > button {
        width: 100% !important;
        padding: 0.7rem;
        background: #3498db;
        border: none;
        border-radius: 6px;
        color: white;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* (The rest of your CSS is perfect and doesn't need changes) */
    .stButton > button:hover { background: #2980b9; }
    .stTextArea > div > div > textarea { background: #ffffff !important; border: 1px solid #ecf0f1 !important; border-radius: 6px !important; color: #2c3e50 !important; }
    .stDownloadButton > button { background: #2ecc71; border: none; border-radius: 6px; color: white; font-weight: 500; padding: 0.6rem 1rem; }
    .stDownloadButton > button:hover { background: #27ae60; }
    .metric-card { background: #f9fbfd; padding: 0.6rem; border-radius: 6px; text-align: center; border: 1px solid #ecf0f1; }
    .metric-value { font-size: 1.1rem; font-weight: 500; color: #2c3e50; }
    .metric-label { color: #7f8c8d; font-size: 0.75rem; margin-top: 0.2rem; }
</style>

  
""", unsafe_allow_html=True)

# (The rest of your Python code is perfect, no changes needed there)

# ---------- Transcript Utilities ----------
def clean_vtt(vtt_content):
    """Clean VTT file content into plain transcript text."""
    no_tags = re.sub(r'<[^>]+>', '', vtt_content)
    lines = no_tags.strip().split('\n')
    clean_lines = [
        line.strip() for line in lines
        if line.strip() and not line.startswith('WEBVTT')
        and '-->' not in line and not line.startswith('Kind:')
    ]
    seen = set()
    unique_lines = [x for x in clean_lines if not (x in seen or seen.add(x))]
    clean_text = ' '.join(unique_lines)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text

def fetch_transcript_text(video_url, lang_code='en'):
    """Fetch transcript from YouTube using yt-dlp."""
    # Using a unique temp file name to avoid conflicts if multiple users access the app
    temp_filename_base = f"transcript_{int(time.time())}_{hash(video_url)}"
    
    try:
        command = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", lang_code,
            "--skip-download",
            "-o", temp_filename_base,
            video_url
        ]
        subprocess.run(command, capture_output=True, text=True, timeout=60, check=True)

        vtt_files = glob.glob(f"{temp_filename_base}*.vtt")
        if not vtt_files:
            return f"Error: No transcript found for '{lang_code}'. Check subtitle availability."

        with open(vtt_files[0], 'r', encoding='utf-8') as f:
            vtt_content = f.read()

        clean_text = clean_vtt(vtt_content)
        if not clean_text:
            return f"Error: Transcript for '{lang_code}' is empty."

        return clean_text

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        if "no subtitles available" in error_message.lower():
            return f"Error: No subtitles available for '{lang_code}'."
        return f"Error running yt-dlp: {error_message}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
    finally:
        # Clean up any transcript files that were created
        for f in glob.glob(f"{temp_filename_base}*.vtt"):
            os.remove(f)

# --- Streamlit UI ---
with st.container():
    st.markdown("""
    <h1 class="main-title">🎬 YouTube Transcript Fetcher</h1>
    <p class="subtitle">Extract and download transcripts effortlessly</p>
    """, unsafe_allow_html=True)

    youtube_url = st.text_input(
        "🔗 YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    language_options = {
        "English": "en", "Spanish": "es", "French": "fr", "German": "de",
        "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
        "Korean": "ko", "Chinese": "zh", "Romanian": "ro"
    }

    selected_language_display = st.selectbox(
        "🌐 Select Language",
        options=list(language_options.keys()),
    )

    if st.button("Fetch Transcript", use_container_width=True):
        if youtube_url:
            lang_code = language_options[selected_language_display]
            with st.spinner(f'Fetching {selected_language_display} transcript...'):
                transcript = fetch_transcript_text(youtube_url, lang_code=lang_code)
                
                if transcript.startswith("Error:"):
                    st.error(transcript)
                else:
                    word_count = len(transcript.split())
                    char_count = len(transcript)
                    estimated_read_time = max(1, round(word_count / 200)) # Standard reading speed
                    
                    st.markdown("---")
                    st.markdown("### Transcript Stats")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        col1.metric("Words", f"{word_count:,}")
                    with col2:
                        col2.metric("Characters", f"{char_count:,}")
                    with col3:
                        col3.metric("Est. Read Time", f"~{estimated_read_time} min")
                    
                    st.markdown("### Transcript")
                    st.text_area("Full transcript:", transcript, height=300, label_visibility="collapsed")
                    st.download_button(
                        label="⬇️ Download Transcript",
                        data=transcript.encode('utf-8'),
                        file_name="transcript.txt",
                        mime='text/plain',
                        use_container_width=True
                    )
        else:
            st.warning("Please enter a YouTube URL.")

