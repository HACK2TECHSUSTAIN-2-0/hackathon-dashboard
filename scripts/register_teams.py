import os
import time
import json
import re
from pathlib import Path
from github_api import gh

# ---------------- CONFIG ----------------
ORG = "HACK2TECHSUSTAIN-2-0"

BASE_DIR = Path(__file__).resolve().parent.parent
TEAMS_FILE = BASE_DIR / "docs" / "data" / "teams.json"
COUNTER_FILE = BASE_DIR / "config" / "counters.json"

TOKEN = os.environ.get("ORG_ADMIN_TOKEN")
if not TOKEN:
    raise RuntimeError("ORG_ADMIN_TOKEN is not set")

# ------------- INPUT (example) ----------
TEAM_NAME = "4 Pointer"
PROBLEM_SLUG = "smart-agri-green-yield"
MEMBERS = ["mattmurdock1908"]  # GitHub usernames ONLY

# ------------- HELPERS ------------------
def slugify(name):
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-")

# ------------- LOAD COUNTER -------------
counter = json.loads(COUNTER_FILE.read_text())
team_num = counter["next_team_id"]

team_id = f"T{team_num:03d}"
team_slug = slugify(TEAM_NAME)
repo_name = f"{team_id.lower()}-{team_slug}"

# ------------- CREATE REPO --------------
print(f"Creating repo: {repo_name}")

gh(
    "POST",
    f"https://api.github.com/orgs/{ORG}/repos",
    TOKEN,
    json={
        "name": repo_name,
        "private": True,
        "auto_init": True
    }
)

# GitHub consistency delay (VERY IMPORTANT)
time.sleep(3)

# ------------- ADD OUTSIDE COLLABS -------
for username in MEMBERS:
    print(f"Inviting outside collaborator: {username}")

    gh(
        "PUT",
        f"https://api.github.com/repos/{ORG}/{repo_name}/collaborators/{username}",
        TOKEN,
        json={"permission": "push"}
    )

# ------------- UPDATE FILES --------------
teams = {}
if TEAMS_FILE.exists():
    teams = json.loads(TEAMS_FILE.read_text())

teams[team_id] = {
    "team_name": TEAM_NAME,
    "team_slug": team_slug,
    "repo": repo_name,
    "members": MEMBERS
}

TEAMS_FILE.parent.mkdir(parents=True, exist_ok=True)
TEAMS_FILE.write_text(json.dumps(teams, indent=2))

counter["next_team_id"] += 1
COUNTER_FILE.write_text(json.dumps(counter, indent=2))

print("✅ Team registered successfully")
