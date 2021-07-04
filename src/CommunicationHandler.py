import pyttsx3
import speech_recognition as sr
import sys


class CommunicationHandler:
    def __init__(self, blind, deaf, dumb):
        self.AUDIO_IN = not dumb
        self.AUDIO_OUT = not deaf
        self.VIDEO_IN = not blind and (deaf or dumb)
        self.VIDEO_OUT = not blind
        if not ((self.AUDIO_IN or self.VIDEO_IN) and (self.AUDIO_OUT or self.VIDEO_OUT)):
            print("Questa modalità non è supportata")
            sys.exit(-5)

        self.voice = pyttsx3.init()
        self.mic = sr.Microphone()
        self.ear = sr.Recognizer()
        self.voice.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_IT-IT_ELSA_11.0')

    def say(self, text):
        if self.VIDEO_OUT:
            print(text)
        if self.AUDIO_OUT:
            self.voice.say(text)
            self.voice.runAndWait()

    def listen(self):

        if self.AUDIO_IN:
            tentative = 0
            while tentative < 3:
                tentative += 1
                with self.mic as source:
                    audio = self.ear.listen(source)

                    try:
                        text = self.ear.recognize_google(audio, language="it-IT")
                        print("Google Speech Recognition crede che tu abbia detto " + text)
                        return text.lower()
                    except sr.UnknownValueError:
                        self.say("Non ho capito, potresti ripetere?")
                    except sr.RequestError as e:
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return input("Scrivi qui ").lower()

