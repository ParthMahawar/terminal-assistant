import openai
import os
import sys
import json

openai.api_key = "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"

def run_terminal_command(command):
    print(command)
    os.system(command)

functions = [
    {
        "name": "run_terminal_command",
        "description": "Runs a terminal command for the specified action the user intends to take",
        "parameters":{
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The terminal command to execute, e.g. If the user wants to list all files in the current folder, ls",
                },
            },
            "required": ["command"]
        }
    }
]

messages = [
    {"role": "user",
     "content": sys.argv[1]}
]

response = openai.ChatCompletion.create(
    model= "gpt-3.5-turbo-0613", #"gpt-4-0613",
    messages=messages,
    functions=functions,
    function_call="auto",  # auto is default, but we'll be explicit
)

response_message = response["choices"][0]["message"]

if response_message.get("function_call"):
    function_args = json.loads(response_message["function_call"]["arguments"])
    command = function_args.get("command")

    run_terminal_command(command)


else:
    print(response)
