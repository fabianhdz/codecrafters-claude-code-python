import subprocess
import sys



def runReadTool(args: dict) -> str:
    
    with open(args["file_path"], "r") as f:
        return f.read() 

def runWriteTool(args: dict):

    with open(args["file_path"], "w", encoding="utf-8") as f:
        f.write(args["content"])
    return "Created the file"

def runBashTool(args: dict):
    print(args["command"], file=sys.stderr)
    output = subprocess.run(args["command"], shell=True, capture_output=True, text=True)

    if output.returncode:
        return output.stderr
    return output.stdout
    
def executeTool(name: str, args):
    if name == "Read":
        return runReadTool(args)
    elif name == "Write":
        return runWriteTool(args)
    elif name == "Bash":
        return runBashTool(args)
    raise ValueError(f"Unknown function: {name}")