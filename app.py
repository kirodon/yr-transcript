import streamlit as st
import subprocess
import os
import re

def clean_vtt(vtt_content):
    """
    Removes timestamps and metadata from a VTT file content,
    and combines lines of text.
    """
    lines = vtt_content.strip().split('\n')
    # Filter out VTT metadata lines (like WEBVTT, timestamps)
    text_lines = [line for line in lines if not line.startswith('WEBVTT') and not '-->' in line and line.strip()]
    
    # Remove duplicate lines while preserving order
    seen = set()
    unique_lines = [x for x in text_lines if not (x in seen or seen.add(x))]
    
    return ' '.join(unique_lines)

def fetch_transcript_text(video_url):
    """
    Uses yt-dlp to download the transcript, read it, and then clean it up.
    This is a much more reliable method for cloud environments.
    """
    # Use a unique filename in a temp directory if possible, but for Streamlit, a simple name is fine
    output_filename = "downloaded_transcript.en.vtt"
    
    try:
        # Command to download the English auto-caption, in .vtt format
        command = [
            "yt-dlp",
            "--write-auto-sub",      # Get the automatically generated subtitles
            "--sub-lang", "en",      # Specify English
            "--skip-download",       # Don't download the video itself
            "-o", "downloaded_transcript", # Specify the base output name
            video_url
        ]

        # Run the command. Capture output to check for errors.
        result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=True)

        # Check if the file was actually created
        if not os.path.exists(output_filename):
            return f"Error: yt-dlp ran but did not create the subtitle file. The video might not have an English transcript."

        # Read the content of the downloaded .vtt file
        with open(output_filename, 'r', encoding='utf-8') as f:
            vtt_content = f.read()

        # Clean the VTT content to get only the spoken text
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
        # CRITICAL: Clean up the downloaded file
        if os.path.exists(output_filename):
            os.remove(output_filename)


# --- Streamlit Web App Interface ---
st.set_page_config(page_title="YouTube Transcript Fetcher", layout="centered")
st.title("YouTube Transcript Fetcher")
st.write("This tool uses `yt-dlp` for robust transcript fetching. Paste a YouTube URL below.")

youtube_url = st.text_input("Enter YouTube URL:", placeholder="e.g., https://www.youtube.com/watch?v=zBlvV0W4bDc")

if st.button("Get Transcript"):
    if youtube_url:
        with st.spinner('Fetching transcript using yt-dlp... This may take a moment.'):
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
