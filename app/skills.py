import os
import yaml
import re
import sys

from pathlib import Path


def parseYaml(path, section):

    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()

    if text.startswith("---"):
        content = text.split("---", 2)
    

    if section == "frontmatter":
        yaml_data = content[1]
        metadata = yaml.safe_load(yaml_data)

    else: # section is body 
        return content[2]

    
    return metadata

def getSkillsNames() -> list[str]:

    dir_path = Path(".claude/skills")
    if not dir_path.exists():
        return []
    skills_names = []
    for item in dir_path.iterdir():
        if item.is_dir():
            skills_names.append(item.name)

    return skills_names

def getSkills() -> list[str]:

    skills_names = getSkillsNames()
    skills = []
    for skill in skills_names:

        skillPath = f".claude/skills/{skill}/SKILL.md"
        frontmatter = parseYaml(skillPath, "frontmatter")
        skills.append(f"- {frontmatter["name"]} (located at {skillPath}): {frontmatter["description"]}\n")

    return skills

def parseBody(text, arguments):
    if arguments is None:
        arguments = []

    idx = 0
    arg_list = []
    while(True):
        '''
        Find arguments types:
        $ARGUMENTS
        $ARGUMENTS[0], $ARGUMENTS[1], ..
        $0, $1, $2, …
        '''
        dollar_idx = text.find("$", idx)
        if dollar_idx == -1:
            break

        idx = dollar_idx + 1
        match = re.match(r'ARGUMENTS(?:\[\d+\])?|\d+', text[idx:])

        if match:
            arg = match.group() 
            if arg == "ARGUMENTS":
                arg_list.append((idx, arg))
            elif '[' in arg and ']' in arg and "ARGUMENTS" in arg:
                arg_list.append((idx, arg))
            elif arg.isdigit():
                arg_list.append((idx, arg))
                
    index_sum = 0
    for idx, arg in arg_list:
        if arg == "ARGUMENTS":
            replacement = " ".join(arguments)

        elif '[' in arg and ']' in arg and "ARGUMENTS" in arg:
            digit = re.search(r'\d+',arg)
            if digit:
                i = int(digit.group())
            replacement = arguments[i]
        else:
            i = int(arg)
            replacement = arguments[i]

        placeholder = "$" + arg
        start = index_sum + idx - 1
        text = text[:start] + replacement + text[start + len(placeholder):]
        index_sum += len(replacement) - len(placeholder)

    return text

    


def getSkillBody(skillName, arguments):

    skillPath = f".claude/skills/{skillName}/SKILL.md"
    body = parseYaml(skillPath, "body")
    text = parseBody(body, arguments)
    return text

        
    

