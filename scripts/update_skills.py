import re
import requests
from pathlib import Path
from urllib.parse import quote

SKILLS_URL = "https://raw.githubusercontent.com/Jishnu314/web/main/src/data/skills.js"
BADGE_COLOR = "2C2D72"

src = requests.get(SKILLS_URL, timeout=30).text

# Grab every "items: [...]" array and collect the strings inside
skills = []
for block in re.findall(r"items:\s*\[(.*?)\]", src, re.S):
    skills += re.findall(r'"([^"]+)"', block)

# Remove duplicates, keep order
seen, unique = set(), []
for s in skills:
    if s not in seen:
        seen.add(s)
        unique.append(s)

def badge(name):
    label = name.replace("-", "--").replace("_", "__")
    label = quote(label, safe="")
    return f"![{name}](https://img.shields.io/badge/{label}-{BADGE_COLOR}?style=flat-square)"

section = "\n".join(badge(s) for s in unique)
block = f"<!-- SKILLS:START -->\n{section}\n<!-- SKILLS:END -->"

readme = Path("README.md")
text = readme.read_text(encoding="utf-8")
text = re.sub(r"<!-- SKILLS:START -->.*?<!-- SKILLS:END -->", block, text, flags=re.S)
readme.write_text(text, encoding="utf-8")
print(f"Updated with {len(unique)} skills")