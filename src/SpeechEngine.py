import pyttsx3
import speech_recognition as sr
class SpeechEngine:
    def __init__(self):
        self.voice = pyttsx3.init()
        self.mic = sr.Microphone()
        self.ear = sr.Recognizer()

    def say(self, text):
        print(text)
        self.voice.say(text)
        self.voice.runAndWait()

    def listen(self):
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

        return None