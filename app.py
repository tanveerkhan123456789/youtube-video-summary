import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator

load_dotenv()  # Load all the environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the prompt
prompt = """
You are a YouTube video summarizer. You will be taking the transcript text and summarizing the entire video and providing the important summary in points within 250 words.
"""

# Function to extract transcript details from YouTube videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1].split("&")[0]  # Ensure video ID extraction handles multiple parameters
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = ' '.join([entry['text'] for entry in transcript_text])
        return full_transcript
    except Exception as e:
        raise e

# Function to generate summary using Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + "\n\n" + transcript_text)
        print("Response Object:", response)  # Debugging: Inspect response object
        # Validate response structure
        if response and hasattr(response, 'text'):
            return response.text
        else:
            raise ValueError("The response object does not contain a 'text' attribute or is malformed")
    except Exception as e:
        raise e

# Function to translate text to Urdu using Google Translate
def translate_to_urdu(text):
    try:
        translator = Translator()
        translation = translator.translate(text, dest='ur')
        return translation.text
    except Exception as e:
        raise e

# Streamlit interface
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1].split("&")[0]  # Ensure video ID extraction handles multiple parameters
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    try:
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
            try:
                english_summary = generate_gemini_content(transcript_text, prompt)
                urdu_summary = translate_to_urdu(english_summary)
                st.markdown("## Detailed Notes in Urdu:")
                st.write(urdu_summary)
            except Exception as e:
                st.error(f"Error generating summary: {e}")
        else:
            st.error("No transcript found for the given YouTube video.")
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
