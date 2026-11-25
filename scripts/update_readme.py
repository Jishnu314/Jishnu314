import os, re, requests
from pathlib import Path

USER = os.environ["GH_USER"]
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
MAX_DEPTH = 2
IGNORE = {".git", "node_modules", "__pycache__", ".github"}

def get(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def tree_for(repo):
    data = get(f"https://api.github.com/repos/{USER}/{repo['name']}/git/trees/{repo['default_branch']}?recursive=1")
    paths = []
    for item in data.get("tree", []):
        parts = item["path"].split("/")
        if len(parts) > MAX_DEPTH or any(p in IGNORE for p in parts):
            continue
        paths.append(item["path"])
    lines = [f"{repo['name']}/"]
    for p in sorted(paths):
        depth = p.count("/")
        lines.append("│   " * depth + "├── " + p.split("/")[-1])
    return "\n".join(lines)

def build_section(repos):
    out = []
    for r in repos:
        desc = r["description"] or "No description yet."
        lang = r["language"] or "—"
        out.append(
            f"<details>\n"
            f"<summary><b>{r['name']}</b> · ⭐ {r['stargazers_count']} · {lang}</summary>\n\n"
            f"{desc}\n\n"
            f"```text\n{tree_for(r)}\n```\n\n"
            f"[View repo]({r['html_url']})\n"
            f"</details>\n"
        )
    return "\n".join(out)

repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated&type=public")
repos = [r for r in repos if not r["fork"] and r["name"] != USER]

readme = Path("README.md")
text = readme.read_text(encoding="utf-8")
new_block = f"<!-- REPOS:START -->\n{build_section(repos)}\n<!-- REPOS:END -->"
text = re.sub(r"<!-- REPOS:START -->.*?<!-- REPOS:END -->", new_block, text, flags=re.S)
readme.write_text(text, encoding="utf-8")
print(f"Updated with {len(repos)} repos")