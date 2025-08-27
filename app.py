import streamlit as st
import subprocess
import os
import re
import time

# Configure the page with a minimalist theme
st.set_page_config(
    page_title="YouTube Transcript Fetcher",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS to neutralize default markdown without hiding content
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Neutralize default Streamlit markdown container */
    .stMarkdown {
        padding: 0 !important;
        margin: 0 !important;
        background: none !important;
    }
    [data-testid="stMarkdownContainer"] {
        padding: 0 !important;
        margin: 0 !important;
        background: none !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
        font-family: 'Roboto', sans-serif;
    }
    
    .main-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 1.5rem;
        background: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-top: 0;
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
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        max-width: 100% !important;
        width: 100% !important;
        background: #ffffff !important;
        border: 1px solid #ecf0f1 !important;
        border-radius: 6px !important;
        color: #2c3e50 !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 0.9rem !important;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within {
        border-color: #3498db !important;
    }
    
    .stTextInput > label, .stSelectbox > label {
        color: #2c3e50 !important;
        font-weight: 400 !important;
        margin-bottom: 0.4rem !important;
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
        transition: background 0.3s ease;
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
    
    .stDownloadButton > button {
        background: #2ecc71;
        border: none;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        padding: 0.6rem 1rem;
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
        padding: 0.6rem;
        border-radius: 6px;
        text-align: center;
        border: 1px solid #ecf0f1;
    }
    
    .metric-value {
        font-size: 1.1rem;
        font-weight: 500;
        color: #2c3e50;
    }
    
    .metric-label {
        color: #7f8c8d;
        font-size: 0.75rem;
        margin-top: 0.2rem;
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
            return f"Error: No transcript found for '{lang_code}'. Check if subtitles are available."
        with open(output_filename, 'r', encoding='utf-8') as f:
            vtt_content = f.read()
        clean_text = clean_vtt(vtt_content)
        if not clean_text:
            return f"Error: Transcript for '{lang_code}' is empty or unreadable."
        return clean_text
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        if "no subtitles available" in error_message.lower():
            return f"Error: No subtitles available for '{lang_code}'."
        return f"Error running yt-dlp: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)

# Use a container to encapsulate all content
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("""
    <h1 class="main-title">🎬 YouTube Transcript Fetcher</h1>
    <p class="subtitle">Extract and download transcripts effortlessly</p>
    """, unsafe_allow_html=True)

    st.markdown('<p style="color: #2c3e50; font-weight: 400; margin-bottom: 0.4rem;">🔗 YouTube Video URL</p>', unsafe_allow_html=True)
    youtube_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        label_visibility="collapsed"
    )
    
    st.markdown('<p style="color: #2c3e50; font-weight: 400; margin-bottom: 0.4rem; margin-top: 1rem;">🌐 Select Language</p>', unsafe_allow_html=True)
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
        index=0,  # Default to "English"
        label_visibility="collapsed",
        key="language_select"
    )
    st.write(f"Debug: Selected language - {selected_language} ({language_options[selected_language]})")  # Debug output
    
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
    <div style="text-align: center; color: #7f8c8d; padding: 0.5rem; font-size: 0.85rem;">
        <p>Fast and reliable transcript extraction</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
