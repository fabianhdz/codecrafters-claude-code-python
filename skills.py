import os
import yaml

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
        skills.append(f"- {frontmatter["name"]}: {frontmatter["description"]}\n")

    return skills


def getSkillBody(skillName):

    skillPath = f".claude/skills/{skillName}/SKILL.md"
    body = parseYaml(skillPath, "body")

    return body

        
    

