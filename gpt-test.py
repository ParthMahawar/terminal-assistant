import openai
import os
import sys
import json
from pytube import YouTube
from pytube import Search
import random


openai.api_key = "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"

def run_terminal_command(fargs):
    command = fargs.get("command")
    print(command)
    os.system(command)

def play_yt_vid_from_search(fargs):
    search_term = fargs.get("search_term")
    rnd = fargs.get("random")
    s = Search(search_term)
    if rnd == None:
        vid = s.results[0]
    else:
        vid = s.results[random.randint(0, len(s.results)-1)]

    print(f"firefox https://youtube.com/watch?v={vid.video_id}")
    print(search_term)
    print(rnd)
    os.system(f"firefox https://youtube.com/watch?v={vid.video_id}")

def google_search(fargs):
    search_term = fargs.get("search_term")
    search_term = search_term.replace(" ", "+")
    print(search_term)
    os.system(f"firefox https://www.google.com/search?q={search_term}")

functions = [
    {
        "name": "run_terminal_command",
        "description": "Runs all the instructions specified by the user in one single terminal command",
        "parameters":{
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The terminal command to execute that executes all instructions, e.g. If the user wants to list all files in the current folder, ls",
                },
            },
            "required": ["command"]
        }
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
        "description": "Opens a Google Search window, only use when user asks for info GPT does not have, like sports scores",
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

messages = [
    {"role": "user",
     "content": sys.argv[1]}
]

response = openai.ChatCompletion.create(
    model= "gpt-4-0613",#"gpt-3.5-turbo-0613",
    messages=messages,
    functions=functions,
    function_call="auto",  # auto is default, but we'll be explicit
)

response_message = response["choices"][0]["message"]

if response_message.get("function_call"):
    available_functions = {
        "run_terminal_command":run_terminal_command,
        "play_yt_vid_from_search":play_yt_vid_from_search,
        "google_search":google_search
    }
    function_name = response_message["function_call"]["name"]
    function_to_call = available_functions[function_name]
    function_args = json.loads(response_message["function_call"]["arguments"])

    function_to_call(function_args)
else:
    print(response)
