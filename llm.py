import json
import requests

import json


from home_API import Home
import asyncio
import re


import click
import torch
import speech_recognition as sr
from typing import Optional

from whisper_mic import WhisperMic
GLOBAL_RESULT = ""

from flask import Flask, request, jsonify
import threading
import json
import time

app = Flask(__name__)

# Shared variable to store user input
user_input = None
response_get = None
w_flag = True

input_received_event = threading.Event()
response_ready_event = threading.Event()

device_info = {'SamsungTV': 'TV In living room. This is not a light!',
'Soundbar': 'Soundbar in living room',
'SmartThings Hub - Soundbar': "Not a DEvice to be controlled",
'LivingroomLight2': 'Living room light  - near sofa and kitchen',
'BedroomLight2': 'Bed room light - near bed',
'livingroomlight1': 'Living room light - near TV',
'bedroomlight1': 'Bedroom light - away from bed'
}

device_keys = [k.lower() for k in device_info]
device_info = dict(zip(device_keys,device_info.values()))
print(device_info)

command_info = {"turn_on" : "turn on given device",
                    "turn_off": "turn off given device"}


# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = 'solar' # TODO: update this for whatever model you wish to use

async def parse_response(response,h):
    global response_get

# Regular expression pattern to match device:command pairs
    pattern = re.compile(r'(\w+):(\w+)')

# Find all matches in the string
    device_commands = pattern.findall(response)
    print("Parsed Response : ",device_commands)
    response_get = device_commands
    response_ready_event.set()
    # Parse and execute each command

    for device_command in device_commands:

        device, command = device_command
        device = device.replace(" ","")
        command = command.replace(" ","")
        device = device.lower()
        if device not in device_info.keys() :
            print(device, " not in devices list. Try again.")
            continue
        elif command not in command_info.keys():
            print(command, " not in command list. Try again.")
            continue

        await h(device,command)
        print(f"{device} has been sent a {command} command!")


async def generate(prompt, context,h):
    global response_get
    print("TYPE OF PROMPT:", type(prompt))
    ip = '192.168.1.185'
    p = '5001'
    r = requests.post(f'http://{ip}:{p}/api/generate',json={
                          'model': model,
                          'prompt': prompt,
                          'context': context,
                      },
                      stream=True)
    r.raise_for_status()
    res_str = ''
    for line in r.iter_lines():
        body = json.loads(line)
        response_part = body.get('response', '')
        # the response streams one token at a time, print that as we receive it
        res_str+=response_part
        print(response_part, end='', flush=True)
        # await parse_response(response_part,h)

        if 'error' in body:
            raise Exception(body['error'])

        if body.get('done', False):
            if 'justin' not in user_input.lower():
                response_get = res_str
                response_ready_event.set()
            
            await parse_response(res_str,h) #uncomment this to control devices!!!!!
            return body['context']
           

async def main():
    global user_input
    global w_flag
    h = Home()
    await h.st_initiate()
    h.initiate()
    print("instantiated devices")
    
    device_info_str = json.dumps(device_info)
    command_info_str = json.dumps(command_info)

    pretext = "Given the following dictionary of devices and commands, reply 'devicename:command'. \
               Your reply should consist of two words - 'devicename:command' "
            # " # the context stores a conversation history, you can use this to make the model more context aware
    context = []
    try:
        while True:
            print("Waiting for command Beech...")
            # audio = record_audio()
            # if  w_flag == True:
            #     time.sleep(0.01)
            #     continue
            input_received_event.wait()
            # user_input = transcribe_audio(audio)
            # user_input = receive_text()
            # user_input = "Turn off bedroom lights"
            # print("GOT INPUT FROM IPHONE:",user_input)
            # instantiate_whisper()
            print()
            if 'justin' in user_input.lower():
                user_input = pretext + device_info_str + command_info_str + "; Answer the question: " + str(user_input) 


            # # print("USER INPUT IS :",user_input)
            context = await generate(user_input, context,h)
            # w_flag = True
            input_received_event.clear()
            response_ready_event.clear()
            # print()
    except KeyboardInterrupt:
        print("Main thread interrupted and exiting...")


@app.route('/text', methods=['POST'])
def receive_text():
    global user_input
    global response_get
    print("RECEIVE TEXT WORKING")
    text_value = request.get_json()
    print(text_value)
    if text_value.get('command'):
        user_input = text_value.get('command')

        input_received_event.set()
        response_ready_event.wait()
        return jsonify({"reply": response_get})
    else:
        print('No valid posted command')
        return jsonify({"reply": "Your message here"})
    
    

def run_flask_app():
    app.run(host='192.168.1.185', port=5000, debug=False)



if __name__ == "__main__":
    
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True  # Daemon threads are abruptly stopped when the main program exits
    flask_thread.start()
    asyncio.run(main()) 




