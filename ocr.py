import requests
import cv2

class OCR:

    def __init__(self, endpoint="", api_key=""):
        self.endpoint = endpoint
        self.key = api_key
        
    # function to recognize text in an image
    def recognize_text(self, img):
        text = ""

        headers = {                                                             # definisco l'header della richiesta                                            
            'Ocp-Apim-Subscription-Key': self.key,                              # inserisco la chiave dell'API
            'Content-Type': 'application/octet-stream'  
        }

        url  = self.endpoint + 'computervision/imageanalysis:analyze?api-version=2023-02-01-preview&features=read'

        _, img_encoded = cv2.imencode('.jpg', img)
        response = requests.post(url, headers=headers, data=img_encoded.tobytes())

        if response.status_code == 200:
            text = response.json()['readResult']['content'].replace('\n', ' ')
        else:
            print('Error')
            print(response.status_code)
            print(response.text)

        return text
    # function to extract the title and the author of a book from a text
    def getInfo(self, text):
        author = ""
        title = ""
        headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Content-Type': 'application/json'
        }

        url = self.endpoint + 'text/analytics/v3.2-preview.1/entities/recognition/general'

        data = {
            'documents': [
                {
                    'id': '1',
                    'text': text
                }
            ]
        }
        response = requests.post(url, headers=headers, json=data)    
        data = response.json()
        
        print(data)
        if len(data['documents']) != 0:
            if len(data['documents'][0]['entities']) != 0:
                for entity in data['documents'][0]['entities']:
                    if entity['category'] == 'Person':
                        author = entity['text']
                        break

        title = text.replace(author, "").strip()
        return title, author