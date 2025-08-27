import streamlit as st
import subprocess
import os
import re
import time

# Configure the page with a modern theme
st.set_page_config(
    page_title="YouTube Transcript Fetcher",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a cooler UX
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(135deg, #6b48ff 0%, #00ddeb 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 2.5rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        margin-top: 3rem;
        margin-bottom: 3rem;
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main-title {
        font-size: 3.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.5rem;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.85);
        text-align: center;
        margin-bottom: 3.5rem;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        color: #1a1a1a !important;
        font-size: 1.1rem !important;
        padding: 1.4rem 1.8rem !important;
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00ddeb !important;
        box-shadow: 0 0 0 3px rgba(0, 221, 235, 0.3) !important;
    }
    
    .stTextInput > label, .stSelectbox > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        margin-bottom: 0.7rem !important;
        font-size: 1rem !important;
    }
    
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        color: #1a1a1a !important;
    }
    
    .stButton > button {
        width: 100%;
        padding: 1.5rem;
        background: linear-gradient(135deg, #00ddeb 0%, #6b48ff 100%);
        border: none;
        border-radius: 20px;
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        transition: all 0.4s ease;
        box-shadow: 0 10px 30px rgba(107, 72, 255, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(107, 72, 255, 0.5);
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        color: #1a1a1a !important;
        backdrop-filter: blur(12px);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #6b48ff 0%, #00ddeb 100%);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 600;
        padding: 1rem 2rem;
        transition: all 0.4s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 30px rgba(107, 72, 255, 0.4);
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #00ddeb 0%, #6b48ff 100%);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1) !important;
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1rem;
        margin-top: 0.6rem;
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
<p class="subtitle">Extract transcripts with a futuristic vibe</p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    st.markdown('<p style="color: #ffffff; font-weight: 600; margin-bottom: 0.7rem;">🔗 YouTube Video URL</p>', unsafe_allow_html=True)
    youtube_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        label_visibility="collapsed"
    )
    
    st.markdown('<p style="color: #ffffff; font-weight: 600; margin-bottom: 0.7rem; margin-top: 1.5rem;">🌐 Select Language</p>', unsafe_allow_html=True)
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
    
    if st.button("✨ Fetch Transcript", use_container_width=True):
        if youtube_url:
            progress_bar = st.progress(0)
            status_text = st.empty()
            for i in range(20):
                progress_bar.progress(i * 5)
                status_text.text(f"🔄 Processing... {i * 5}%")
                time.sleep(0.1)
            
            with st.spinner('🎯 Fetching transcript...'):
                transcript = fetch_transcript_text(youtube_url, lang_code=language_options[selected_language])
                
                progress_bar.progress(100)
                status_text.text("✅ Done!")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                if transcript.startswith("Error:"):
                    st.error(f"❌ {transcript}")
                else:
                    word_count = len(transcript.split())
                    char_count = len(transcript)
                    estimated_read_time = max(1, word_count // 200)
                    
                    st.markdown("### 📊 Transcript Stats")
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.markdown('<div class="metric-card"><div class="metric-value">{:,}</div><div class="metric-label">Words</div></div>'.format(word_count), unsafe_allow_html=True)
                    with metric_col2:
                        st.markdown('<div class="metric-card"><div class="metric-value">{:,}</div><div class="metric-label">Characters</div></div>'.format(char_count), unsafe_allow_html=True)
                    with metric_col3:
                        st.markdown('<div class="metric-card"><div class="metric-value">{}</div><div class="metric-label">Est. Read Time</div></div>'.format(f"{estimated_read_time} min"), unsafe_allow_html=True)
                    
                    st.markdown("### 📝 Transcript")
                    trans_col1, trans_col2 = st.columns([4, 1])
                    with trans_col1:
                        st.text_area(
                            "Full transcript:",
                            transcript,
                            height=450,
                            label_visibility="collapsed"
                        )
                    with trans_col2:
                        st.download_button(
                            label="⬇️ Download",
                            data=transcript.encode('utf-8'),
                            file_name="transcript.txt",
                            mime='text/plain',
                            use_container_width=True
                        )
        else:
            st.warning("⚠️ Please enter a YouTube URL.")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255, 255, 255, 0.7); padding: 0.5rem; font-size: 1rem;">
    <p>Fast & reliable • 10+ languages supported</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
