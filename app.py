import streamlit as st
import subprocess
import os
import re
import time
import shutil
import glob

# Configure the page with your theme
st.set_page_config(page_title="YouTube Transcript Fetcher", page_icon="🎬", layout="centered")

# --- THIS IS THE FULL, CORRECT CSS BLOCK ---
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

    .stSelectbox div[data-baseweb="select"] {
        background: #ffffff !important;
        border: 1px solid #ecf0f1 !important;
        border-radius: 6px !important;
        font-size: 0.95rem !important;
        padding: 0.1rem 0.4rem !important;
    }
    .stSelectbox div[data-baseweb="select"] > div > div {
        color: #2c3e50 !important;
        background-color: transparent !important;
    }
    
    /* This rule makes the main button blue */
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
    
    .stButton > button:hover {
        background: #2980b9;
    }
    
    .stTextArea > div > div > textarea {
        background: #ffffff !important;
        border: 1px solid #ecf0f1 !important;
        border-radius: 6px !important;
        color: #2c3e50 !important;
    }
    
    /* This rule makes the download button green */
    .stDownloadButton > button {
        background: #2ecc71;
        border: none;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        padding: 0.6rem 1rem;
    }
    
    .stDownloadButton > button:hover {
        background: #27ae60;
    }
</style>
""", unsafe_allow_html=True)

# --- Python Logic (Unchanged and Correct) ---

def clean_vtt(vtt_content):
    no_tags = re.sub(r'<[^>]+>', '', vtt_content)
    lines = no_tags.strip().split('\n')
    clean_lines = [
        line.strip() for line in lines
        if line.strip() and not line.startswith('WEBVTT')
        and '-->' not in line 
        and not line.startswith('Kind:')
        and not line.startswith('Language:')
    ]
    seen = set()
    unique_lines = [x for x in clean_lines if not (x in seen or seen.add(x))]
    clean_text = ' '.join(unique_lines)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text

def fetch_transcript_text(video_url):
    base_filename = f"transcript_{int(time.time())}_{hash(video_url)}"
    lang_code = 'en'
    debug_info = {}
    try:
        command = [
            "yt-dlp", "--write-sub", "--write-auto-sub",
            "--sub-lang", lang_code, "--skip-download",
            "-o", base_filename, video_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        debug_info['yt_dlp_stdout'] = result.stdout.strip()
        debug_info['yt_dlp_stderr'] = result.stderr.strip()
        debug_info['exit_code'] = result.returncode
        vtt_files = glob.glob(f"{base_filename}*.{lang_code}.vtt")
        if not vtt_files:
            return f"ERROR: English transcript file not found.", debug_info
        with open(vtt_files[0], 'r', encoding='utf-8') as f:
            vtt_content = f.read()
        clean_text = clean_vtt(vtt_content)
        if not clean_text:
            return f"ERROR: Transcript is empty.", debug_info
        return clean_text, debug_info
    except Exception as e:
        return f"ERROR: A Python exception occurred: {str(e)}", debug_info
    finally:
        for f in glob.glob(f"{base_filename}*.vtt"):
            os.remove(f)

# --- Final Streamlit UI ---

with st.container():
    st.markdown("""
    <h1 class="main-title">🎬 YouTube Transcript Fetcher</h1>
    <p class="subtitle">Extract and download English transcripts effortlessly</p>
    """, unsafe_allow_html=True)

    youtube_url = st.text_input(
        "🔗 YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )
    
    if st.button("Fetch Transcript", use_container_width=True):
        if youtube_url:
            with st.spinner('Fetching English transcript...'):
                transcript, debug_info = fetch_transcript_text(youtube_url)
                
                if transcript.startswith("ERROR:"):
                    st.error("Failed to retrieve transcript. This often means an English transcript does not exist for this video.")
                    with st.expander("Click to see technical details"):
                        st.code(f"""
                        yt-dlp Exit Code: {debug_info.get('exit_code', 'N/A')}
                        --- Standard Output (stdout) ---
                        {debug_info.get('yt_dlp_stdout', 'No output captured.')}
                        --- Standard Error (stderr) ---
                        {debug_info.get('yt_dlp_stderr', 'No output captured.')}
                        """)
                else:
                    st.success("Transcript fetched successfully!")
                    st.text_area("Full transcript:", transcript, height=300)
                    st.download_button(
                        label="⬇️ Download Transcript",
                        data=transcript.encode('utf-8'),
                        file_name="transcript.txt",
                        mime='text/plain',
                        use_container_width=True
                    )
        else:
            st.warning("Please enter a YouTube URL.")
