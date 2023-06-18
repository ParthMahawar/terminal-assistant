import openai
import subprocess
import json

# Replace with your OpenAI API Key
openai.api_key = 'API_KEY'

def terminal_command_executor(command):
    """Execute a terminal command and return the output"""
    result = subprocess.run(command, capture_output=True, shell=True, text=True)
    return {"output": result.stdout, "error": result.stderr}

def run_conversation():
    available_functions = {
        "terminal_command_executor": terminal_command_executor,
    }

    functions = [
        {
            "name": "terminal_command_executor",
            "description": "Execute a terminal command and return the output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The terminal command to execute, that executes all instructions, e.g. If the user wants to list all files in the current folder, ls"},
                },
                "required": ["command"],
            },
        }
    ]

    messages = []
    while True:
        user_prompt = input("GPT-Assistant: ")
        messages.append({"role": "user", "content": user_prompt})

        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
            functions=functions,
            function_call="auto",  # auto is default, but we'll be explicit
        )

        response_message = response["choices"][0]["message"]
        
        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            
            print(f"Command to execute: {function_args.get('command')}")
            confirmation = input("Are you sure you want to execute this command? (y/n): ")

            if confirmation.lower() == 'y':
                function_response = function_to_call(
                    command=function_args.get("command"),
                )

                messages.append(response_message)  # extend conversation with assistant's reply
                messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response
                second_response = openai.ChatCompletion.create(
                    model="gpt-4-0613",
                    messages=messages,
                )  # get a new response from GPT where it can see the function response
                
                assistant_message = second_response["choices"][0]["message"]["content"]
                print(f"Assistant Response: {assistant_message}")
            else:
                print("Command execution cancelled.")

run_conversation()
