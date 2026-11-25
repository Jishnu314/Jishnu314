import re
import requests
from pathlib import Path
from urllib.parse import quote

SKILLS_URL = "https://raw.githubusercontent.com/Jishnu314/web/main/src/data/skills.js"

# One color per skill group (matched by group name)
GROUP_COLORS = {
    "Programming Languages": "2C2D72",
    "Industrial Automation & Control": "0B7285",
    "PLC & SCADA Software": "1A6DB4",
    "Embedded Systems & IoT": "2B8A3E",
    "Engineering Tools": "B45309",
    "Development Tools": "495057",
}
DEFAULT_COLOR = "343A40"

src = requests.get(SKILLS_URL, timeout=30).text

# Find each group and its items, keeping the group name for the color
groups = re.findall(r'group:\s*"([^"]+)".*?items:\s*\[(.*?)\]', src, re.S)

def badge(name, color):
    label = name.replace("-", "--").replace("_", "__")
    label = quote(label, safe="")
    return f"![{name}](https://img.shields.io/badge/{label}-{color}?style=flat-square)"

lines = []
seen = set()
for group, block in groups:
    color = GROUP_COLORS.get(group, DEFAULT_COLOR)
    for name in re.findall(r'"([^"]+)"', block):
        if name in seen:
            continue
        seen.add(name)
        lines.append(badge(name, color))

section = "\n".join(lines)
block = f"<!-- SKILLS:START -->\n{section}\n<!-- SKILLS:END -->"

readme = Path("README.md")
text = readme.read_text(encoding="utf-8")
text = re.sub(r"<!-- SKILLS:START -->.*?<!-- SKILLS:END -->", block, text, flags=re.S)
readme.write_text(text, encoding="utf-8")
print(f"Updated with {len(lines)} skills")
