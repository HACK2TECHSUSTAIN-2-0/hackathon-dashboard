import json
import argparse
import os
import requests

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

def ensure_team(team_slug):
    r = requests.get(
        f"https://api.github.com/orgs/{ORG}/teams/{team_slug}",
        headers=HEADERS
    )

    if r.status_code == 200:
        return

    if r.status_code == 404:
        gh(HEADERS, "POST", f"/orgs/{ORG}/teams", json={
            "name": team_slug,
            "privacy": "secret"
        })
        return

    raise RuntimeError(f"Team check failed: {r.status_code} {r.text}")


def ensure_repo(repo_name, description):
    r = requests.get(
        f"https://api.github.com/repos/{ORG}/{repo_name}",
        headers=HEADERS
    )

    if r.status_code == 200:
        # Update description if repo exists
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

    ps_id = r.get("PS ID")
    ps = r.get("PS")

    repo_name = slugify(team_name)
    team_slug = f"team-{team_id.lower()}"

    description = f"TeamID: {team_id} | PS: {ps or 'Not assigned'}"

    # 1️⃣ Team
    ensure_team(team_slug)

    # 2️⃣ Members
    for user in usernames:
        gh(
            HEADERS,
            "PUT",
            f"/orgs/{ORG}/teams/{team_slug}/memberships/{user}"
        )

    # 3️⃣ Repo
    ensure_repo(repo_name, description)

    # 4️⃣ Permissions
    permission = "push" if ps_id else "pull"
    gh(
        HEADERS,
        "PUT",
        f"/orgs/{ORG}/teams/{team_slug}/repos/{ORG}/{repo_name}",
        json={"permission": permission}
    )

    teams_db[team_id] = {
        "team_name": team_name,
        "repo": repo_name,
        "members": usernames,
        "problem_id": ps_id,
        "problem_title": ps,
        "access": permission
    }

# -------------------------
# SAVE METADATA
# -------------------------

os.makedirs("data", exist_ok=True)
with open("data/teams.json", "w") as f:
    json.dump(teams_db, f, indent=2)

print("Teams successfully registered / updated.")
