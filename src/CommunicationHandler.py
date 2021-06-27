import pyttsx3
import speech_recognition as sr
import sys
class CommunicationHandler:
    def __init__(self, blind, deaf, dumb):
        self.voice = pyttsx3.init()
        self.mic = sr.Microphone()
        self.ear = sr.Recognizer()

        self.AUDIO_IN = not dumb
        self.AUDIO_OUT = not deaf
        self.VIDEO_IN = not blind and (deaf or dumb)
        self.VIDEO_OUT = not blind
        if not ((self.AUDIO_IN or self.VIDEO_IN) and (self.AUDIO_OUT or self.VIDEO_OUT)):
            print("Sorry, I cannot support this modality")
            sys.exit(-5)

    def say(self, text):
        if self.VIDEO_OUT:
            print(text)
        if self.AUDIO_OUT:
            self.voice.say(text)
            self.voice.runAndWait()

    def listen(self):
        if self.AUDIO_IN:
            while True:
                with self.mic as source:
                    audio = self.ear.listen(source)
                    # recognize speech using Google Speech Recognition
                    try:
                        # for testing purposes, we're just using the default API key
                        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                        # instead of `r.recognize_google(audio)`
                        print("Google Speech Recognition thinks you said " + self.ear.recognize_google(audio))
                        return self.ear.recognize_google(audio).lower()
                    except sr.UnknownValueError:
                        self.say("Google Speech Recognition could not understand audio, please could you repeat?")
                    except sr.RequestError as e:
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        else:
            return input("Write here ").lower()