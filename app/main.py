import argparse
import os
import sys
import json
import subprocess

from pathlib import Path
from collections import deque
from openai import OpenAI

from .skills import getSkills, getSkillBody
from .tools import executeTool


API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")
            


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()


    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    model = "anthropic/claude-haiku-4.5"
    skills = getSkills()
    messages =  [
                    {"role": "system", "content": f"You have access to the following:\n\n{"".join(skills)}"},
                ]
    arguments = args.p.split()

    if arguments[0][0] == '/': 
        params = deque()
        for arg in arguments[::-1]:

            if arg[0] == '/':
                file_path =  Path(f".claude/skills/{arg[1:]}/SKILL.md")
                if file_path.is_file():
                    print(arg, file=sys.stderr)
                    skillBody = getSkillBody(arg[1:], list(params)) #/skill, arguments
                    messages.append({"role": "user", "content": skillBody})
                    continue

            params.appendleft(arg)
    else:
        messages.append({"role": "user", "content": args.p})



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
