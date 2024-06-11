from flask import Flask, request, jsonify
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

import time
import speech_recognition as sr
from moviepy.editor import VideoFileClip

app = Flask(__name__)

def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')
    video.close()  # Ensure the video file is closed

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

@app.route('/video', methods=['POST'])
def transcribe_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    video_path = os.path.join('./temp_videos', video_file.filename)
    audio_path = os.path.splitext(video_path)[0] + '.wav'

    os.makedirs('./temp_videos', exist_ok=True)
    os.makedirs('./audios', exist_ok=True)

    video_file.save(video_path)
    extract_audio(video_path, audio_path)
    transcription = transcribe_audio(audio_path)

    # Ensure the video file is properly closed before attempting to delete it
    time.sleep(1)  # Add a short delay to ensure file release

    os.remove(video_path)
    os.remove(audio_path)

    return jsonify({'transcription': transcription})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
