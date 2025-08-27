import streamlit as st
import subprocess
import os
import re
import time
import shutil
import glob

# --- Your beautiful CSS is unchanged ---
st.set_page_config(page_title="YouTube Transcript Fetcher", page_icon="🎬", layout="centered")
st.markdown("""<style>
    /* ... (all of your existing CSS goes here) ... */
</style>""", unsafe_allow_html=True) # Keep your full CSS block

# --- THIS IS THE MODIFIED CLEANING FUNCTION ---
def clean_vtt(vtt_content):
    """Clean VTT file content into plain transcript text."""
    no_tags = re.sub(r'<[^>]+>', '', vtt_content)
    lines = no_tags.strip().split('\n')
    clean_lines = [
        line.strip() for line in lines
        if line.strip() and not line.startswith('WEBVTT')
        and '-->' not in line 
        and not line.startswith('Kind:')
        and not line.startswith('Language:') # <-- ADDED THIS LINE to remove the language tag
    ]
    seen = set()
    unique_lines = [x for x in clean_lines if not (x in seen or seen.add(x))]
    clean_text = ' '.join(unique_lines)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text

def fetch_transcript_text(video_url):
    """
    Fetch English transcript using the final, most robust yt-dlp command.
    """
    base_filename = f"transcript_{int(time.time())}_{hash(video_url)}"
    lang_code = 'en' # We now hardcode English here
    debug_info = {}

    try:
        command = [
            "yt-dlp",
            "--write-sub",
            "--write-auto-sub",
            "--sub-lang", lang_code, # This will always be 'en'
            "--skip-download",
            "-o", base_filename,
            video_url
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

# --- THIS IS THE SIMPLIFIED UI ---
with st.container():
    st.markdown("""
    <h1 class="main-title">🎬 YouTube Transcript Fetcher</h1>
    <p class="subtitle">Extract and download English transcripts effortlessly</p>
    """, unsafe_allow_html=True)

    youtube_url = st.text_input(
        "🔗 YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    # We have completely removed the language selection dropdown
    
    if st.button("Fetch Transcript", use_container_width=True):
        if youtube_url:
            with st.spinner('Fetching English transcript...'): # Simplified message
                # The function now returns two values: the result and the debug info
                transcript, debug_info = fetch_transcript_text(youtube_url)
                
                if transcript.startswith("ERROR:"):
                    st.error(f"Failed to retrieve transcript. This often means an English transcript does not exist for this video.")
                    
                    with st.expander("Click here to see technical details"):
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
