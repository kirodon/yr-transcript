import streamlit as st
import subprocess
import os
import re # <-- Added this important line

def clean_vtt(vtt_content):
    """
    A more robust function to clean VTT content.
    - Removes all HTML-like tags and timestamps using regex.
    - Removes VTT metadata lines.
    - Removes duplicate lines of text.
    """
    # Use a regular expression to find and remove all tags like <...>
    no_tags = re.sub(r'<[^>]+>', '', vtt_content)
    
    # Process the text line by line now
    lines = no_tags.strip().split('\n')
    
    clean_lines = []
    for line in lines:
        # Skip VTT metadata and empty lines
        if line.strip() and not line.startswith('WEBVTT') and '-->' not in line:
            clean_lines.append(line.strip())

    # Remove duplicate lines while preserving the order
    seen = set()
    unique_lines = [x for x in clean_lines if not (x in seen or seen.add(x))]
    
    # Join the unique lines to form the final transcript
    return ' '.join(unique_lines)

def fetch_transcript_text(video_url):
    """
    Uses yt-dlp to download the transcript, read it, and then clean it up.
    """
    output_filename = "downloaded_transcript.en.vtt"
    
    try:
        command = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--skip-download",
            "-o", "downloaded_transcript",
            video_url
        ]

        result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=True)

        if not os.path.exists(output_filename):
            return "Error: yt-dlp ran but did not create the subtitle file. The video might not have an English transcript."

        with open(output_filename, 'r', encoding='utf-8') as f:
            vtt_content = f.read()

        # This now calls our new and improved cleaning function
        clean_text = clean_vtt(vtt_content)
        
        return clean_text

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        if "no subtitles available" in error_message.lower():
            return "Error: This video does not have subtitles available in English."
        return f"Error running yt-dlp: {error_message}"
    except subprocess.TimeoutExpired:
        return "Error: The download process timed out."
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)

# --- Streamlit Web App Interface (No changes needed here) ---
st.set_page_config(page_title="YouTube Transcript Fetcher", layout="centered")
st.title("YouTube Transcript Fetcher")
st.write("This tool uses `yt-dlp` for robust transcript fetching. Paste a YouTube URL below.")

youtube_url = st.text_input("Enter YouTube URL:", placeholder="e.g., https://www.youtube.com/watch?v=zBlvV0W4bDc")

if st.button("Get Transcript"):
    if youtube_url:
        with st.spinner('Fetching and cleaning transcript...'):
            transcript = fetch_transcript_text(youtube_url)
            if transcript.startswith("Error:"):
                st.error(transcript)
            else:
                st.subheader("Transcript:")
                st.text_area("Full transcript:", transcript, height=300)
                st.download_button(
                    label="Download Transcript as .txt",
                    data=transcript.encode('utf-8'),
                    file_name="transcript.txt",
                    mime='text/plain'
                )
    else:
        st.warning("Please enter a YouTube URL first.")
