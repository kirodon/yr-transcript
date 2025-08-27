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

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom container */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    
    /* Title styling */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.1);
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.8);
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    /* Input styling - Better contrast */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 16px !important;
        color: #333 !important;
        font-size: 1rem !important;
        padding: 1.2rem 1.5rem !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(0, 0, 0, 0.5) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ff6b6b !important;
        background: rgba(255, 255, 255, 0.95) !important;
        box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2) !important;
    }
    
    /* Input label styling */
    .stTextInput > label {
        color: white !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Selectbox styling - Better visibility */
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 16px !important;
        color: #333 !important;
    }
    
    .stSelectbox > div > div > div > div {
        color: #333 !important;
    }
    
    .stSelectbox > label {
        color: white !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    .stButton > button {
        width: 100%;
        padding: 1.3rem;
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
        border: none;
        border-radius: 16px;
        color: white;
        font-size: 1.1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px rgba(255, 107, 107, 0.4);
    }
    
    /* Text area styling - Better visibility */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 16px !important;
        color: #333 !important;
        backdrop-filter: blur(10px);
    }
    
    .stTextArea > label {
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 0.8rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 25px rgba(79, 172, 254, 0.4);
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning {
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #ff6b6b;
    }
    
    /* Metrics styling - Better visibility */
    .metric-card {
        background: rgba(255, 255, 255, 0.2) !important;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        flex: 1;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* Metric containers from Streamlit */
    .css-1r6slb0 {
        background: rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .css-1r6slb0 .metric-value {
        color: white !important;
        font-size: 1.8rem !important;
        font-weight: bold !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Better styling for metric elements */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    [data-testid="metric-container"] > div {
        color: white !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
    }
</style>
""", unsafe_allow_html=True)

def clean_vtt(vtt_content):
    """
    A more robust function to clean VTT content.
    - Removes all HTML-like tags and timestamps using regex.
    - Removes VTT metadata lines.
    - Removes duplicate lines of text.
    """
    no_tags = re.sub(r'<[^>]+>', '', vtt_content)
    lines = no_tags.strip().split('\n')
    
    clean_lines = []
    for line in lines:
        # This is the line we're updating. We're adding "and not line.startswith('Kind:')"
        if line.strip() and not line.startswith('WEBVTT') and '-->' not in line and not line.startswith('Kind:'):
            clean_lines.append(line.strip())
    seen = set()
    unique_lines = [x for x in clean_lines if not (x in seen or seen.add(x))]
    
    return ' '.join(unique_lines)

def fetch_transcript_text(video_url, lang_code='en'):
    """
    Uses yt-dlp to download the transcript for a specific language.
    """
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
            return f"Error: Could not find a transcript for the language '{lang_code}'. The video might not have one."
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

# Main UI
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
<h1 class="main-title">🎬 YouTube Transcript Fetcher</h1>
<p class="subtitle">Extract transcripts from YouTube videos with style</p>
""", unsafe_allow_html=True)

# Create columns for better layout
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Input field with visible label
    st.markdown('<p style="color: white; font-weight: 600; margin-bottom: 0.5rem;">🔗 YouTube Video URL</p>', unsafe_allow_html=True)
    youtube_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        label_visibility="collapsed"
    )
    
    # Language selection with visible label
    st.markdown('<p style="color: white; font-weight: 600; margin-bottom: 0.5rem; margin-top: 1rem;">🌐 Select Language</p>', unsafe_allow_html=True)
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
    
    # Main action button
    if st.button("✨ Fetch Transcript", use_container_width=True):
        if youtube_url:
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Animated progress
            for i in range(20):
                progress_bar.progress(i * 5)
                status_text.text(f"🔄 Processing... {i * 5}%")
                time.sleep(0.1)
            
            with st.spinner('🎯 Fetching and cleaning transcript...'):
                transcript = fetch_transcript_text(youtube_url, lang_code=language_options[selected_language])
                
                # Complete progress
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                if transcript.startswith("Error:"):
                    st.error(f"❌ {transcript}")
                else:
                    # Success state with metrics
                    word_count = len(transcript.split())
                    char_count = len(transcript)
                    estimated_read_time = max(1, word_count // 200)  # Average reading speed
                    
                    # Display metrics in a nice grid
                    st.markdown("### 📊 Transcript Statistics")
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.metric("Words", f"{word_count:,}")
                    with metric_col2:
                        st.metric("Characters", f"{char_count:,}")
                    with metric_col3:
                        st.metric("Est. Read Time", f"{estimated_read_time} min")
                    
                    # Display transcript
                    st.markdown("### 📝 Transcript")
                    transcript_container = st.container()
                    
                    with transcript_container:
                        # Create two columns for transcript and download
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
                                label="⬇️ Download",
                                data=transcript.encode('utf-8'),
                                file_name="transcript.txt",
                                mime='text/plain',
                                use_container_width=True
                            )
                            
                            # Additional export options
                            st.markdown("---")
                            st.markdown("**Export Options:**")
                            
                            # Word format (simulated)
                            if st.button("📄 Word Format", use_container_width=True):
                                st.info("💡 Tip: Copy the text and paste into Word!")
                            
                            # JSON format
                            if st.button("🔧 JSON Format", use_container_width=True):
                                import json
                                json_data = {
                                    "transcript": transcript,
                                    "language": selected_language,
                                    "url": youtube_url,
                                    "word_count": word_count,
                                    "char_count": char_count
                                }
                                st.download_button(
                                    "Download JSON",
                                    data=json.dumps(json_data, indent=2),
                                    file_name="transcript.json",
                                    mime="application/json"
                                )
        else:
            st.warning("⚠️ Please enter a YouTube URL first.")

# Remove the ugly footer and replace with cleaner version
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255, 255, 255, 0.7); padding: 0.5rem; font-size: 0.9rem;">
    <p>Fast & reliable transcript extraction • Supports 10+ languages</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
