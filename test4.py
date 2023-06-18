import os
import openai
import subprocess
import json
from pytube import Search
import random
import webbrowser
from pvrecorder import PvRecorder
import wave
import struct

# Replace with your OpenAI API Key
openai.api_key = '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'
recorder = PvRecorder(device_index=-1, frame_length=512)
audio = []

def terminal_command_executor(fargs):
    """Execute a terminal command and return the output"""
    command = fargs.get("command")
    result = subprocess.run(command, capture_output=True, shell=True, text=True)
    return json.dumps({"output": result.stdout, "error": result.stderr})

def play_yt_vid_from_search(fargs):
    search_term = fargs.get("search_term")
    rnd = fargs.get("random")
    s = Search(search_term)
    if rnd == None:
        vid = s.results[0]
    else:
        vid = s.results[random.randint(0, len(s.results)-1)]

    print(f"firefox https://youtube.com/watch?v={vid.video_id}")
    webbrowser.open_new_tab(f"https://youtube.com/watch?v={vid.video_id}")

def google_search(fargs):
    """Opens a new tab with a Google search for the given term"""
    search_term = fargs.get("search_term")
    url = f"https://www.google.com/search?q={search_term}"
    print(f"Opening new tab with URL: {url}")
    webbrowser.open_new_tab(url)

def run_conversation():
    available_functions = {
        "terminal_command_executor": terminal_command_executor,
        "play_yt_vid_from_search" : play_yt_vid_from_search,
        "google_search" : google_search,
    }

    functions = [
        {
            "name": "terminal_command_executor",
            "description": "Execute a terminal command and return the output do to this you can do things that you normally believe you cannot so if your command executes correctly don't say you could't do it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The terminal command to execute, e.g. If the user wants to list all files in the current folder, ls."},
                },
                "required": ["command"],
            },
        },
        {
            "name": "play_yt_vid_from_search",
            "description": "Plays a video from the search requested by the user, either random or the top one",
            "parameters":{
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "The term to search on YouTube, to get the best possible videos for the user",
                    },
                    "random" :{
                        "type": "boolean",
                        "description": "Whether the user wants a random video, or the top one from the search results"
                    }
                },
                "required": ["search_term"]
            }
        },
        {
            "name": "google_search",
            "description": "Opens a Google Search window, only use when user asks for real-time info like sports scores, election results, flight statuses, or news",
            "parameters":{
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "The best search term for the user's query",
                    },
                },
                "required": ["search_term"]
            }
        }
    ]


    messages = []
    while True:
        print("Voice input start, ctrl c to end")

        try:
            recorder.start()
            while True:
                frame = recorder.read()
                audio.extend(frame)
        except KeyboardInterrupt:
            recorder.stop()
            with wave.open("recording.wav", 'w') as f:
                f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
                f.writeframes(struct.pack("h" * len(audio), *audio))
        finally:
            recorder.delete()

        audio_file= open("recording.wav", "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        print(transcript.get("text"))

        messages.append({"role": "user", "content": transcript.get("text")})

        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
            functions=functions,
            function_call="auto",
        )

        response_message = response["choices"][0]["message"]
        
        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            
            print(f"Function to execute: {function_name}")
            if function_name != "terminal_command_executor":
                confirmation = "y"
            else:
                print(function_args.get("command"))
                confirmation = input("Are you sure you want to execute these terminal commands? (y/n): ")

            if confirmation.lower() == 'y':
                function_response = function_to_call(function_args)
                
                if function_response is not None:
                    if function_name == "terminal_command_executor":
                        function_response_json = json.loads(function_response)
                        if 'error' in function_response_json and function_response_json['error']:
                            print("Error executing command:", function_response_json['error'])
                        else:
                            print("Command output:", function_response_json['output'])
                    messages.append(
                        {
                            "role": "function",
                            "name": function_name,
                            "content": function_response,
                        }
                    )
                    
                messages.append(response_message)  # extend conversation with assistant's reply
                
                if function_name == "terminal_command_executor":
                    second_response = openai.ChatCompletion.create(
                        model="gpt-4-0613",
                        messages=messages,
                    )
                    
                    assistant_message = second_response["choices"][0]["message"]["content"]
                    print(f"Response: {assistant_message}")
            else:
                print("Function execution cancelled.")

run_conversation()