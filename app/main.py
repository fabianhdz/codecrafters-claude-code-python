import argparse
import os
import sys
import json
import subprocess

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")



def runReadTool(args: dict) -> str:
    
    with open(args["file_path"], "r") as f:
        return f.read() 

def runWriteTool(args: dict):

    with open(args["file_path"], "w", encoding="utf-8") as f:
        f.write(args["content"])
    return "Created the file"

def runBashTool(args: dict):
    return subprocess.run(args["command"], capture_output=True)

def executeTool(name: str, args):
    if name == "Read":
        return runReadTool(args)
    elif name == "Write":
        return runWriteTool(args)
    elif name == "Bash":
        return runWriteTool(args)
    raise ValueError(f"Unknown function: {name}")
            


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    model = "anthropic/claude-haiku-4.5"
    messages = [{"role": "user", "content": args.p}]

    tools = [
                {
                    "type": "function",  
                      "function": {
                           "name": "Read", 
                           "description": "Read and return the content of a file",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "file_path": {
                                        "type": "string",
                                        "description": "The path of the file to read"
                                    }
                                },
                            "required": ["file_path"]
                        } 
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "Write",
                        "description": "Write content to a file",
                        "parameters": {
                            "type:": "object",
                            "required": ["file_path", "content"],
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path of the file to write to",
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The content to write to the file",
                                }
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "Bash",
                        "description": "Execute a shell command",
                        "parameters" : {
                            "type": "object",
                            "required" : ["command"],
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "descripton": "The command to execute"
                                }
                            }
                        }
                    }
                },
            ]

    
    while(True):

        chat = client.chat.completions.create(
                model = model,
                messages = messages,
                tools = tools
            )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        # You can use print statements as follows for debugging, they'll be visible when running tests.
        print("Logs from your program will appear here!", file=sys.stderr)


        if not chat.choices[0].message.tool_calls:
            print(chat.choices[0].message.content)
            break
        else:
            for tool in chat.choices[0].message.tool_calls:
                args = json.loads(tool.function.arguments)
                result = executeTool(tool.function.name, args)

                usage = {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool.id,
                                "type": tool.type,
                                "function": tool.function,
                            },
                        ]
                }
                output = {
                            "role": "tool",
                            "tool_call_id": tool.id,
                            "content": result
                }
                messages.append(usage)
                messages.append(output)
   




if __name__ == "__main__":
    main()
