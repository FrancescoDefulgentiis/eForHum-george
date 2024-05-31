import requests

class Chatbot:

    def __init__(self, endpoint="", bot_key="", model=""):
        self.key = bot_key
        self.endpoint = endpoint
        self.model = model
        self.prompt = {
            "messages":[

                # The first message is the prompt that the model will use to generate the response
                {"role": "system", 
                 "content": "Comportati come un esperto di letteratura."+
                            " Rispondi alle domande fornendo informazioni bibliografiche e riassunti del libro e dell'autore specificati dall'user."+
                            " Rispondi alle domande in modo umile, sintetico e professionale."+
                            " Concludi ogni frase con una domanda"+
                            " Formula la risposta in massimo 75 parole."
                            }                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
            ]
        }
        
    # function that returns the response of the chatbot given an input
    def ask(self, input, log = True): 
        
        if log:
            self.prompt["messages"].append({"role": "user", "content": input})                                  # add the user input to the prompt
        
        headers= {                                                                                              # set the headers for the request
                "Content-Type":"application/json",  
                "api-key":self.key
                }

        url=f"{self.endpoint}openai/deployments/{self.model}/chat/completions?api-version=2023-03-15-preview"   # set the url for the request

        res= requests.post(url,headers=headers,json=self.prompt)                                                # send the request to the chatbot
        
        if res.status_code == 200:                                                                              # if the request is successful
            response = res.json()["choices"][0]["message"]["content"]                                           # get the response from the chatbot
            if log:
                self.prompt["messages"].append({"role": "assistant", "content": response})                      # log the response to the prompt
            return response 
        else:
            print(res.json())                                                                                   # print the error

    # function to insert a message in the prompt
    def insert_message(self, role, content):
        self.prompt["messages"].append({"role": role, "content": content})                                      # add the user input to the prompt
            
    
    