from faceRecognition import FaceRecognition
from speechRecognition import SpeechRecognition
from dotenv import load_dotenv
from chatbot import Chatbot
from ocr import OCR
import cv2
import os
import threading

load_dotenv()

OCR_clicked = False
Speak_clicked = False
Exit_clicked = False
flag  = False

def draw_ui(frame):    
    height, width, _ = frame.shape  # Obtain the shape of the frame
    text_area_height = 50           # Set the dimension of the text area
    button_height = 50              # Set the dimension of the buttons
    button_width = width // 2 - 10  # Since there are 3 buttons we divide the width by 3

    # Draw the 3 buttons
    cv2.rectangle(frame, (10, height - button_height - 10), (10 + button_width, height - 10), (82, 75, 74), -1)
    text_width, _ = cv2.getTextSize("OCR", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    text_x = (button_width // 2) - (text_width // 2)
    cv2.putText(frame, "OCR", (text_x, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.rectangle(frame, (width // 2 + 10, height - button_height - 10), (width // 2 + 10 + button_width, height - 10), (0,0,255), -1)
    text_width, _ = cv2.getTextSize("Exit", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    text_x = (width // 2 + button_width // 2) - (text_width // 2)
    cv2.putText(frame, "Exit", (text_x, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    return frame


# Function that given a mouse event, checks wich button was clicked
def button_click(event, x, y, flags, param):
    global OCR_clicked, Speak_clicked, Exit_clicked
    height, width = param                   # Obtain the height and width from the parameters

    button_height = 50                      
    button_width = width // 2 - 10

    if event == cv2.EVENT_LBUTTONDOWN:      # Check if the event is a left button click
        if y > height - button_height - 10: # Check if the click is in the first button area
            if x < button_width:
                OCR_clicked = True
            else:                           # Check if the click is in the third button area
                Exit_clicked = True


if __name__ == '__main__':
    api_endpoint = os.getenv('API_ENDPOINT')
    bot_endpoint = os.getenv('BOT_ENDPOINT')
    api_key = os.getenv('API_KEY')
    bot_key = os.getenv('BOT_KEY')
    region = os.getenv('REGION')

    bot = Chatbot(endpoint=bot_endpoint, bot_key=bot_key, model="gpt-35-turbo")
    sr = SpeechRecognition(api_key=api_key, location=region)
    ocr = OCR(endpoint=api_endpoint, api_key=api_key)
    fr = FaceRecognition(endpoint=api_endpoint, api_key=api_key)

    cap = cv2.VideoCapture(0)
    
    _, frame = cap.read()
    height, width, _ = frame.shape                                          # Obtain the shape of the frame
    state=0                                                                 # Set the initial state to 0
    george= cv2.imread("George.jpeg")                                         # Load the image of the book
    frame = cv2.resize(george, (width, height))

    temp = cv2.cvtColor(george, cv2.COLOR_BGR2GRAY)

    cv2.namedWindow("Chatbot Interface")
    cv2.setMouseCallback("Chatbot Interface", button_click, (height, width))    # Set the mouse callback function

    while True:                                                                 # Main loop          
        _, cam = cap.read()                                                     # Read the frame from the camera

        if Exit_clicked:                                                        # Check if the exit button was clicked
            break

        if state == 0:                                                          # State is 0

            if not fr.detect_faces(cam):                                        # Check if a face is detected
                print("no face detected")
            else:
                if fr.confirm_detection(cam):                                   # Check if the face is confirmed
                    print("face detected")
                    sr.Say("Ciao, sono George, il tuo esperto di libri. Che lingua parli?") # Say the welcome message
                    bot.insert_message(role="assistant", content="Ciao, sono George, il tuo esperto di libri. Che lingua parli?")
                    richiesta = sr.Listen()                                     # Listen for the user input
                    language = sr.detectLanguage(richiesta)                     # Detect the language of the user input
                    if language != "it":
                        richiesta = sr.Translate(richiesta,destination_language="it", source_language=language)
                    sr.Say("per favore, Dimmi di che libro vuoi parlare, oppure premi il tasto qui sotto per mostrarmelo", language=language)   
                    bot.insert_message(role="assistant", content="per favore, Dimmi di che libro vuoi parlare, oppure premi il tasto qui sotto per mostrarmelo")
                    state = 1   
            
        elif state == 1:                                                                                # State is 1

            richiesta = sr.Listen()                                         # Listen for the user input

            if OCR_clicked:                                                 # Check if the OCR button was clicked
                sr.Say("Mostrami il testo che vuoi riconoscere.", language=language)
                bot.insert_message(role="assistant", content="Mostrami il testo che vuoi riconoscere.")
                count = 0
                list = []
                state = 2
            elif Exit_clicked:                                              # Check if the Exit button was clicked
                break
            else:
                flag = True
                state = 3


        elif state == 2:                                                    # State is 2 (OCR)
            frame = cam                                                     # Set the frame to the camera frame
            cv2.rectangle(cam, (0, 100), (300, 400), (0, 255, 0), 2)        # Draw a green rectangle on the frame
            cropped = cam[100:400, 0:300]                                   # Crop the frame   
            bn = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)                  # Convert the cropped frame to grayscale
            blurred = cv2.GaussianBlur(bn, (7, 7), 0)                       # Apply a Gaussian blur to the cropped frame
            lower = cv2.resize(blurred, (width//10, height//10))            # Resize the cropped frame to the original frame size
            diffs = []  
            for i in range(blurred.shape[0]):
                for j in range(blurred.shape[1]):
                    diffs.append(blurred[i][j] - temp[i][j])                # Calculate the difference between the current frame and the previous frame
            diff = sum(diffs) / len(diffs)                                  # Calculate the average difference
            if(diff < 73):
                read = ocr.recognize_text(cropped)                          # Recognize the text in the cropped frame

                if read != "":                                              # If the text is not empty
                    count += 1  
                    list.append(read)                                       # Append the text to the list
                    if count == 7:                                          # If the count is 7
                        read = max(list, key=list.count)                    # Get the most frequent text
                        text = f"Il libro che mi hai mostrato è {read}, confermi che sia corretto?."
                        frame = cv2.resize(george, (width, height))         # set the frame back to george
                        draw_ui(frame)
                        cv2.imshow("Chatbot Interface", frame)
                        bot.insert_message(role="assistant", content=text)
                        sr.Say(text, language=language)
                        state = 3

            temp = blurred                                                  # Set the temp frame to the blurred frame

            
        elif state == 3:                                                    # State is 3

            if not flag:
                richiesta = sr.Listen()                                     # Listen for the user input
            else: 
                flag = False
        
            if richiesta == "":                                             # If the user input is empty
                break                                                       # Exit the program
            
            if language != "it":
                richiesta = sr.Translate(richiesta,destination_language="it", source_language=language)

            risposta = bot.ask(richiesta)
            sr.Say(risposta, language=language)

        draw_ui(frame)
        cv2.imshow("Chatbot Interface", frame)
        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()