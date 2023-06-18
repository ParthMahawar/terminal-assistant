import os
import openai
import subprocess
import json
from pytube import Search
import random
import webbrowser

# Replace with your OpenAI API Key
openai.api_key = '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'

def terminal_command_executor(fargs):
    """Execute a terminal command and return the output"""
    command = fargs.get("command")
    command = command + " && pwd"
    cwd = fargs.get("cwd")
    result = subprocess.run(command, capture_output=True, shell=True, cwd = cwd, text=True)
    stdout = "\n" + result.stdout[:-1]
    return json.dumps({"output": stdout[:stdout.rfind("\n")], 
                       "error": result.stderr, 
                       "cwd": stdout[stdout.rfind("\n")+1:]})

def play_yt_vid_from_search(fargs):
    search_term = fargs.get("search_term")
    rnd = fargs.get("random")
    s = Search(search_term)
    try:
        if rnd == None:
            vid = s.results[0]
        else:
            vid = s.results[random.randint(0, len(s.results)-1)]
    except:
        print("err")

    try:    
        print(f"Opening new tab with URL: https://youtube.com/watch?v={vid.video_id}")
        webbrowser.open_new_tab(f"https://youtube.com/watch?v={vid.video_id}")
    except:
        print("err")

def google_search(fargs):
    """Opens a new tab with a Google search for the given term"""
    search_term = fargs.get("search_term").replace(" ", "+")
    url = f"https://www.google.com/search?q={search_term}"
    print(f"Opening new tab with URL: {url}")
    webbrowser.open_new_tab(url)

def get_command_explanation(command):
    """Ask GPT-4 to provide an explanation of what the command does"""
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": f"What does the terminal command '{command}' do?"}]
    )
    return response["choices"][0]["message"]["content"]

def run_conversation():
    currpath = os.path.expanduser('~')

    available_functions = {
        "terminal_command_executor": terminal_command_executor,
        "play_yt_vid_from_search" : play_yt_vid_from_search,
        "google_search" : google_search,
    }

    functions = [
        {
            "name": "terminal_command_executor",
            "description": "Runs all the instructions specified by the user in one single MacOS terminal command, use this whenever the user asks for file creation or manipulation as well",
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
        user_prompt = input(f"Shelly @ {currpath} >> ")
        messages.append({"role": "user", "content": user_prompt})

        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
            function_call="auto",
            functions=functions
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
                command = function_args.get("command")
                print(command)
                while True:
                    confirmation = input("Do you want to execute this terminal command? (y/n/h for help): ")
                    if confirmation.lower() == 'h':
                        print(get_command_explanation(command))
                    else:
                        break

            if confirmation.lower() == 'y':
                function_args["cwd"] = currpath
                function_response = function_to_call(function_args)
                
                if function_response is not None:
                    if function_name == "terminal_command_executor":
                        function_response_json = json.loads(function_response)
                        if 'error' in function_response_json and function_response_json['error']:
                            print("Error executing command:", function_response_json['error'])
                        else:
                            print("Command output:", function_response_json['output'])
                            currpath = function_response_json["cwd"]
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