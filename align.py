import os
import subprocess
import speech_recognition as sr

def extract_audio(video_path, audio_path):
    command = f"ffmpeg -i \"{video_path}\" -q:a 0 -map a \"{audio_path}\""
    subprocess.call(command, shell=True)

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

def video_to_align(video_path, align_path):
    # Define the audio file path
    audio_dir = os.path.join(os.path.dirname(video_path), '../audios')
    audio_file_name = os.path.splitext(os.path.basename(video_path))[0] + '.wav'
    audio_path = os.path.join(audio_dir, audio_file_name)
    
    # Ensure the audio directory exists
    os.makedirs(audio_dir, exist_ok=True)
    
    # Extract audio and transcribe
    extract_audio(video_path, audio_path)
    transcription = transcribe_audio(audio_path)
    
    # Write the transcription to the alignment file
    with open(align_path, 'w') as align_file:
        align_file.write(transcription)

if __name__ == "__main__":
    video_path = "./videos/test_video.mp4"
    align_path = "./aligns/output.align"
    video_to_align(video_path, align_path)
