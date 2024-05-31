import cv2
import requests
#from cnn import CNN
from facenet_pytorch import MTCNN

class FaceRecognition:

    def __init__(self, endpoint="", api_key="", location=""):
        self.key = api_key
        self.endpoint = endpoint
        self.mtcnn = MTCNN(keep_all=True)                                     # Initialize MTCNN for face detection
        
    # Function to detect faces in the image using MTCNN ( Multi-Task Convolutional Neural Network)
    def detect_faces(self, img):
        boxes, _ = self.mtcnn.detect(img)                                     # Detect faces in the image

        if boxes is not None:                                                 # If faces are detected
            return True                                                       # Return True
        
        return False                                                          # Return False
    
    # Function to confirm the detection of faces in the image using Azure Face API
    def confirm_detection(self, img):
        url = f'{self.endpoint}face/v1.0/detect/'                             # inizialiaze the url for the request

        params = {                                                            
            'recognitionModel': 'recognition_04'                              # Set the recognition model
        }

        headers = {                                                           # initialize the headers for the request
            'Ocp-Apim-Subscription-Key': self.key,
            'Content-Type': 'application/octet-stream'
        }

        _, buffer = cv2.imencode('.jpg', img)                                 # convert the image to a buffer

        response = requests.post(url, headers=headers, 
                                 params=params, data=buffer.tobytes())

        if response.status_code == 200:                                       # if the request is successful
            return len(response.json()) > 0                                   # return True if faces are detected
        else:
            print(response.json())                                            # print the error

