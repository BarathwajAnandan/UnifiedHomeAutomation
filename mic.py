# import speech_recognition as sr

# def get_audio_input():
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Listening...")
#         audio = r.listen(source)
#         try:
#             text = r.recognize_google(audio)
#             print("You said: {}".format(text))
#             return text
#         except:
#             print("Sorry, I did not get that")
#             return get_audio_input()
        
# get_audio_input()

import sounddevice as sd
import numpy as np
import whisper

# Load the Whisper model
model = whisper.load_model("base")

def record_audio(duration=5, fs=16000):
    """
    Record audio from the microphone for a given duration.
    """
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    return audio.flatten()

def transcribe_audio(audio):
    """
    Transcribe the recorded audio to text using Whisper.
    """
    # Convert the audio to the format expected by Whisper
    audio = whisper.pad_or_trim(audio)
    
    # Transcribe the audio to text
    result = model.transcribe(audio)
    print("Transcribed text:", result['text'])
    return result['text']

# Continuously record and transcribe audio
while True:
    audio = record_audio()
    text = transcribe_audio(audio)
    # Your function to control devices based on the command string
    # control_devices(text)