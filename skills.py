import os
import yaml

from pathlib import Path


def parseYaml(path):

    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()

    if text.startswith("---"):
        content = text.split("---", 2)

    yaml_data = content[1]
    metadata = yaml.safe_load(yaml_data)
    
    return metadata

def getSkillsNames():

    dir_path = Path(".claude/skills")

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
        frontmatter = parseYaml(skillPath)
        skills.append(f"- {frontmatter["name"]}: {frontmatter["description"]}\n")

    return skills

        
    

