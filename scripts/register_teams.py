import json
import argparse
import os
import requests
from pathlib import Path

from excel_reader import read_excel
from utils import slugify
from github_api import gh

ORG = "HACK2TECHSUSTAIN-2-0"

HEADERS = {
    "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github+json"
}

# -------------------------
# HELPERS
# -------------------------

def ensure_repo(repo_name, description):
    r = requests.get(
        f"https://api.github.com/repos/{ORG}/{repo_name}",
        headers=HEADERS
    )

    if r.status_code == 200:
        gh(
            HEADERS,
            "PATCH",
            f"/repos/{ORG}/{repo_name}",
            json={"description": description}
        )
        return

    if r.status_code == 404:
        gh(HEADERS, "POST", f"/orgs/{ORG}/repos", json={
            "name": repo_name,
            "private": True,
            "description": description
        })
        return

    raise RuntimeError(f"Repo check failed: {r.status_code} {r.text}")

# -------------------------
# MAIN
# -------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--excel", required=True)
args = parser.parse_args()

rows = read_excel(args.excel)
teams_db = {}

for r in rows:
    team_id = r["TeamID"].strip().upper()
    team_name = r["Team Name"].strip()
    usernames = [u.strip().lower() for u in r["GitHub Usernames"].split(",")]


    repo_name = slugify(team_name)
    description = f"TeamID: {team_id}"

    # 1️⃣ Repo
    ensure_repo(repo_name, description)

    # 2️⃣ Outside collaborators
    permission = "push"

    for user in usernames:
        gh(
            HEADERS,
            "PUT",
            f"/repos/{ORG}/{repo_name}/collaborators/{user}",
            json={"permission": permission}
        )

    teams_db[team_id] = {
        "team_name": team_name,
        "repo": repo_name,
        "members": usernames,
        "access": permission
    }

# -------------------------
# SAVE METADATA
# -------------------------

OUTPUT_DIR = Path("docs/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_DIR / "teams.json", "w") as f:
    json.dump(teams_db, f, indent=2)

print("Teams successfully registered / updated.")
