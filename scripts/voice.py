#! /usr/bin/env python3

import socket
import speech_recognition as sr     # import the library

# HOST = "192.168.1.11"  # The server's IP address
HOST = "192.168.0.100"  # The server's IP address
PORT = 8084  # The port used by the server

recognizer = sr.Recognizer()                 # initialize recognizer

def recognize_speech():
    global recognizer

    with sr.Microphone() as source:     # mention source it will be  either Microphone or audio files.
        print("Speak Anything :")
        audio = recognizer.listen(source)        # listen to the source
        try:
            text = recognizer.recognize_google(audio)    # use recognizer to convert  our audio into text part.
            print("You said : {}".format(text))
            return text
        except:
            print("Sorry could not recognize your voice")    # In case of  voice not recognized  clearly
            return ''


def send_msg(msg):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(msg.encode())
        print("msg sent: ", msg)

"""
To use real_speech, the PC this program is running needs to be connected to Internet. 
In order to connect to Robot, Robot has to be connected to same wifi as this PC. 
Then IP address needs above need to be changed to the IP address of Robot under this wifi network
"""
real_speech = False

if __name__ == '__main__':
    
    if real_speech: 
        while True:
            msg = recognize_speech()
            print(msg)
            if "stop" in msg: 
                break
            if len(msg) > 0: 
                send_msg(msg)

    else:
        # simulate speech by direct typing in commands
        inp = input("Input your 'speech' command ('quit' to end): \n")
        while inp != 'quit': 
            send_msg(inp)
            inp = input("Input your 'speech' command ('quit' to end): \n")
        
