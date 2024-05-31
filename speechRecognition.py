import os
import requests
import wavio as wv
import sounddevice as sd
from scipy.io.wavfile import write, read

# function to encode special characters
def encode(text):
    return '&#' + str(ord(text)) + ';' 


class SpeechRecognition:
    def __init__(self, api_key="", location=""):
        self.api_key = api_key
        self.location = location

    # function to convert text to speech
    def Say(self, text, language="it"):
        text = text.replace("è", encode("è")).replace("é", encode("é")).replace("à", encode("à")).replace("ò", encode("ò")).replace("ù", encode("ù")).replace("ì", encode("ì")) # encode 
        print(text)
        if language != "it":                                                                            # translate the text to the desired language
            text = self.Translate(text, language)

        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,                                                  # key for the multi-service account
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'cfrmultiservices'
        }

        endpoint = f'https://{self.location}.tts.speech.microsoft.com/cognitiveservices/v1'             # endpoint for the text-to-speech service

        body = f'''<speak version="1.0" xml:lang="it-IT">

                        <voice xml:gender="Male" name="en-US-BrianMultilingualNeural">
                            <lang xml:lang="{language}-{language.upper()}"> {text} </lang>
                        </voice>

                    </speak>'''
        response = requests.post(endpoint, headers=headers, data=body)                                   # send the request to the text-to-speech service

        if response.status_code == 200:
            with open('audio/sample.wav', 'wb') as audio:                                                # save the audio response to a file and play it
                audio.write(response.content)
                rate, audio=read("audio/sample.wav")
                sd.play(audio, samplerate=rate)

                sd.wait()                                                                                # wait for the audio to finish playing
        else:
            print('Error in the request for audio')
            print(response.status_code)


    # function to convert speech to text
    def Listen(self):
        transcription = ""

        # Audio settings
        freq=16000
        duration=7
        fname="audio/audio.wav"

        print("Recording...")
        recording=sd.rec(int(duration*freq), samplerate=freq,channels=1)                                              # Record audio
        sd.wait()
        print("done recording")

        #Write out
        write(fname,freq, recording)                                                                                  # Save the audio to a file
        wv.write(fname, recording, freq, sampwidth=1)   


        url = f'https://{self.location}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1'# endpoint for the speech-to-text service

        headers={
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Content-type':f'codecs=audio/pcm; samplerate={freq}',                                                    # set the headers for the request
            'Accept':'text/json'
        }

        # Set the request parameters
        params = {
            'language': 'it-IT'
        }

        buf=open(fname,"rb")                                                                                          # open the audio file

        response = requests.post(url=url, headers=headers, params=params, data=buf)

        if response.status_code == 200:
            transcription = response.json()['DisplayText']
            print("you said: ", transcription)
        else:
            print('Error in the request for transcription')
            print(response.status_code)
        return transcription
    
    def Translate(self, text, destination_language, source_language="it"):
        translation = ''

        # Use the Translator translate function
        url = f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&"

        params = {
            "from": source_language,
            "to": destination_language
        }

        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Ocp-Apim-Subscription-Region": self.location,
            "Content-Type": "application/json"
        }

        body = [{"text": text}]

        response = requests.post(url, headers=headers, json=body, params=params)
        result = response.json()

        if len(result) > 0:
            translation = result[0]["translations"][0]["text"]

        return translation
    
    def detectLanguage(self, text):
        url = f"https://api.cognitive.microsofttranslator.com/detect?api-version=3.0"

        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Ocp-Apim-Subscription-Region": self.location,
            "Content-Type": "application/json"
        }

        body = [{"text": text}]

        response = requests.post(url, headers=headers, json=body)
        result = response.json()

        if len(result) > 0:
            language = result[0]["language"]

        return language