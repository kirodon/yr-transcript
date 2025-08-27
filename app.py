import streamlit as st
import subprocess
import os
import time

st.set_page_config(
    page_title="YouTube Transcript Fetcher",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background: #f0f4f8;
    }
    .main-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 1.5rem;
        background: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .stMarkdown {
        padding: 0 !important;
        margin: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.write("### 🎬 YouTube Transcript Fetcher")
st.write("Extract and download transcripts effortlessly")

youtube_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
language_options = {"English": "en", "Spanish": "es"}
selected_language = st.selectbox("Select Language", options=list(language_options.keys()), index=0, key="lang_test")
st.write(f"Debug: Selected - {selected_language} ({language_options[selected_language]})")

if st.button("Fetch Transcript"):
    if youtube_url:
        with st.spinner('Fetching...'):
            try:
                command = ["yt-dlp", "--write-auto-sub", "--sub-lang", language_options[selected_language], "--skip-download", "-o", "test", youtube_url]
                st.write(f"Debug: Command - {' '.join(command)}")
                result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=True)
                st.write(f"Debug: Output - {result.stdout}")
                if os.path.exists("test.en.vtt"):
                    with open("test.en.vtt", 'r', encoding='utf-8') as f:
                        transcript = f.read()
                    st.write("Transcript:", transcript)
                else:
                    st.error("No transcript found.")
            except subprocess.CalledProcessError as e:
                st.write(f"Debug: Error - {e.stderr}")
                st.error("Failed to fetch transcript.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
        if os.path.exists("test.en.vtt"):
            os.remove("test.en.vtt")

st.markdown('</div>', unsafe_allow_html=True)
