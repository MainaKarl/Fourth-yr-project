import os
import subprocess
import sys

# Function to install packages from requirements.txt
def install_requirements():
    try:

        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")

# Install requirements
install_requirements()

import speech_recognition as sr
import streamlit as st

def extract_audio(video_path, audio_path):
    command = f"ffmpeg -y -i \"{video_path}\" -q:a 0 -map a \"{audio_path}\""
    subprocess.call(command, shell=True)

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "The Speech Recognition algorithm could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Speech Recognition service; {e}"

def video_to_align(video_path, align_path):
    # Define the audio file path
    audio_dir = os.path.join(os.path.dirname(video_path), '../audios')
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_file_name = video_name + '.wav'
    audio_path = os.path.join(audio_dir, audio_file_name)
    
    # Ensure the audio directory exists
    os.makedirs(audio_dir, exist_ok=True)
    
    # Extract audio and transcribe
    extract_audio(video_path, audio_path)
    transcription = transcribe_audio(audio_path)
    
    # Write the transcription to the alignment file
    with open(align_path, 'w') as align_file:
        align_file.write(transcription)
    
    return transcription

def main():
    # Set the layout to the streamlit app as wide
    st.set_page_config(layout='wide')

    # Setup the sidebar
    with st.sidebar:
        st.title('LipRead')
        st.info('This application is originally developed from the LipNet deep learning model.')

    st.title('Lip Reading App')
    
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
    
    if uploaded_file is not None:
        video_path = f"./temp_videos/{uploaded_file.name}"
        
        # Save the uploaded file to disk
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Uploaded {uploaded_file.name}")

        # Display the video
        st.video(video_path)
        
        # Define the alignment file path
        align_dir = "./aligns"
        os.makedirs(align_dir, exist_ok=True)
        video_name = os.path.splitext(uploaded_file.name)[0]
        align_path = os.path.join(align_dir, f"{video_name}.align")
        
        # Transcribe the video
        transcription = video_to_align(video_path, align_path)
        
        # Display the transcription
        st.header("Transcription")
        st.info("The text below is the words from the video")
        st.text(transcription)
        
        # Clean up the temporary video file
        os.remove(video_path)

if __name__ == "__main__":
    if not os.path.exists("./temp_videos"):
        os.makedirs("./temp_videos")
    if not os.path.exists("./aligns"):
        os.makedirs("./aligns")
    main()
