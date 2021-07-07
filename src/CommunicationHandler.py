import sys

import pyttsx3
import speech_recognition as sr
from pytimedinput import timedInput


class CommunicationHandler:
    def __init__(self, blind, deaf, mute):
        self.AUDIO_IN = not mute
        self.AUDIO_OUT = not deaf
        self.VIDEO_IN = True
        self.VIDEO_OUT = not blind
        if not ((self.AUDIO_IN or self.VIDEO_IN) and (self.AUDIO_OUT or self.VIDEO_OUT)):
            print("Questa modalità non è supportata")
            sys.exit(-5)

        self.voice = pyttsx3.init()
        self.mic = sr.Microphone()
        self.ear = sr.Recognizer()
        self.voice.setProperty('voice',
                               'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_IT-IT_ELSA_11.0')

        self.engine = 0
        self.possible_engines = ["Google", "Sphinx"]

    def say(self, text):
        if self.VIDEO_OUT:
            print(text)
        if self.AUDIO_OUT:
            self.voice.say(text)
            self.voice.runAndWait()

    def listen(self):
        if self.AUDIO_IN:
            attempt = 0
            while attempt < 3:
                attempt += 1
                with self.mic as source:
                    audio = self.ear.listen(source)
                    try:
                        if self.possible_engines[self.engine] == "Sphinx":
                            # recognize speech using Sphinx
                            text = self.ear.recognize_sphinx(audio, language="it-IT")
                        elif self.possible_engines[self.engine] == "Google":
                            # recognize speech using Google Speech Recognition
                            text = self.ear.recognize_google(audio, language="it-IT")
                        print(f"{self.possible_engines[self.engine]} crede che tu abbia detto {text}")
                        if text != "":
                            return text.lower()
                    except sr.UnknownValueError:
                        self.say("Non ho capito, potresti ripetere?")
                    except sr.RequestError as e:
                        print(f"{self.possible_engines[self.engine]} request error; {e}")
        return timedInput("Scrivi qui ", 10)[0].lower()
