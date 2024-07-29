import speech_recognition as sr
from gtts import gTTS
import os
import requests
import pvporcupine
import pyaudio

# Initialize Porcupine
porcupine = pvporcupine.create(
    access_key='your_porcupine_access_key',
    keyword_paths=['path/to/your/wake/word.ppn']
)

# Initialize PyAudio
audio_stream = pyaudio.PyAudio().open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

recognizer = sr.Recognizer()

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("mpg321 response.mp3")

print("Listening for wake word...")

while True:
    pcm = audio_stream.read(porcupine.frame_length)
    pcm = [int.from_bytes(pcm[i:i+2], byteorder='little', signed=True) for i in range(0, len(pcm), 2)]

    # Check for wake word
    keyword_index = porcupine.process(pcm)
    if keyword_index >= 0:
        print("Wake word detected!")
        # Listen for command
        with sr.Microphone() as source:
            print("Listening for command...")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
            response = requests.post('http://localhost:3000/process', json={"input": text}).json()
            print("Response: " + response['response'])
            speak(response['response'])
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
