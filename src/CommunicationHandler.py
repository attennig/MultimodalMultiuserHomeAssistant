import pyttsx3
import speech_recognition as sr
import sys


class CommunicationHandler:
    def __init__(self, blind, deaf, dumb, lang):
        self.AUDIO_IN = not dumb
        self.AUDIO_OUT = not deaf
        self.VIDEO_IN = not blind and (deaf or dumb)
        self.VIDEO_OUT = not blind
        if not ((self.AUDIO_IN or self.VIDEO_IN) and (self.AUDIO_OUT or self.VIDEO_OUT)):
            print("Sorry, I cannot support this modality")
            sys.exit(-5)

        self.voice = pyttsx3.init()
        self.mic = sr.Microphone()
        self.ear = sr.Recognizer()
        assert lang in ["it-IT", "en-EN"]
        self.language = lang
        #for voice in self.voice.getProperty('voices'):
        #    print(voice)
        if self.language == 'it-IT':
            self.voice.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_IT-IT_ELSA_11.0')
            self.say("Ciao, la lingua è stata impostata ad Italiano")

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
                    # recognize speech using Google Speech Recognition
                    try:
                        # for testing purposes, we're just using the default API key
                        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                        # instead of `r.recognize_google(audio)`
                        print("Google Speech Recognition thinks you said " + self.ear.recognize_google(audio, language=self.language))
                        return self.ear.recognize_google(audio).lower()
                    except sr.UnknownValueError:
                        if self.language == "it-IT": self.say("Google Speech Recognition non ha capito, potresti ripetere?")
                        else: self.say("Google Speech Recognition could not understand audio, please could you repeat?")
                    except sr.RequestError as e:
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
                    '''
                    # recognize speech using Sphinx
                    try:
                        print("Sphinx thinks you said " + r.recognize_sphinx(audio))
                    except sr.UnknownValueError:
                        print("Sphinx could not understand audio")
                    except sr.RequestError as e:
                        print("Sphinx error; {0}".format(e))

                    # recognize speech using Google Cloud Speech
                    GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""INSERT THE CONTENTS OF THE GOOGLE CLOUD SPEECH JSON CREDENTIALS FILE HERE"""
                    try:
                        print("Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio,
                                                                                                credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS))
                    except sr.UnknownValueError:
                        print("Google Cloud Speech could not understand audio")
                    except sr.RequestError as e:
                        print("Could not request results from Google Cloud Speech service; {0}".format(e))

                    # recognize speech using Wit.ai
                    WIT_AI_KEY = "INSERT WIT.AI API KEY HERE"  # Wit.ai keys are 32-character uppercase alphanumeric strings
                    try:
                        print("Wit.ai thinks you said " + r.recognize_wit(audio, key=WIT_AI_KEY))
                    except sr.UnknownValueError:
                        print("Wit.ai could not understand audio")
                    except sr.RequestError as e:
                        print("Could not request results from Wit.ai service; {0}".format(e))

                    # recognize speech using Microsoft Bing Voice Recognition
                    BING_KEY = "INSERT BING API KEY HERE"  # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
                    try:
                        print(
                            "Microsoft Bing Voice Recognition thinks you said " + r.recognize_bing(audio, key=BING_KEY))
                    except sr.UnknownValueError:
                        print("Microsoft Bing Voice Recognition could not understand audio")
                    except sr.RequestError as e:
                        print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))

                    # recognize speech using Microsoft Azure Speech
                    AZURE_SPEECH_KEY = "INSERT AZURE SPEECH API KEY HERE"  # Microsoft Speech API keys 32-character lowercase hexadecimal strings
                    try:
                        print(
                            "Microsoft Azure Speech thinks you said " + r.recognize_azure(audio, key=AZURE_SPEECH_KEY))
                    except sr.UnknownValueError:
                        print("Microsoft Azure Speech could not understand audio")
                    except sr.RequestError as e:
                        print("Could not request results from Microsoft Azure Speech service; {0}".format(e))

                    # recognize speech using Houndify
                    HOUNDIFY_CLIENT_ID = "INSERT HOUNDIFY CLIENT ID HERE"  # Houndify client IDs are Base64-encoded strings
                    HOUNDIFY_CLIENT_KEY = "INSERT HOUNDIFY CLIENT KEY HERE"  # Houndify client keys are Base64-encoded strings
                    try:
                        print("Houndify thinks you said " + r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID,
                                                                                 client_key=HOUNDIFY_CLIENT_KEY))
                    except sr.UnknownValueError:
                        print("Houndify could not understand audio")
                    except sr.RequestError as e:
                        print("Could not request results from Houndify service; {0}".format(e))

                    # recognize speech using IBM Speech to Text
                    IBM_USERNAME = "INSERT IBM SPEECH TO TEXT USERNAME HERE"  # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
                    IBM_PASSWORD = "INSERT IBM SPEECH TO TEXT PASSWORD HERE"  # IBM Speech to Text passwords are mixed-case alphanumeric strings
                    try:
                        print("IBM Speech to Text thinks you said " + r.recognize_ibm(audio, username=IBM_USERNAME,
                                                                                      password=IBM_PASSWORD))
                    except sr.UnknownValueError:
                        print("IBM Speech to Text could not understand audio")
                    except sr.RequestError as e:
                        print("Could not request results from IBM Speech to Text service; {0}".format(e))'''

        else:
            return input("Write here ").lower()

