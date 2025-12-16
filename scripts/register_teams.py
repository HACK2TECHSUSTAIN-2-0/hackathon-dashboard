import json
import argparse
import os

from excel_reader import read_excel
from utils import slugify
from github_api import gh

ORG = "HACK2TECHSUSTAIN-2-0"

HEADERS = {
    "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github+json"
}

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

    # 1. Create team (safe if exists)
    gh(HEADERS, "POST", f"/orgs/{ORG}/teams", json={
        "name": team_slug,
        "privacy": "secret"
    })

    # 2. Add members to team
    for user in usernames:
        gh(
            HEADERS,
            "PUT",
            f"/orgs/{ORG}/teams/{team_slug}/memberships/{user}"
        )

    # 3. Create repo (safe)
    description = f"TeamID: {team_id} | PS: {ps or 'Not assigned'}"
    gh(HEADERS, "POST", f"/orgs/{ORG}/repos", json={
        "name": repo_name,
        "private": True,
        "description": description
    })

    # 4. Permission logic
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

# Save metadata
os.makedirs("data", exist_ok=True)
with open("data/teams.json", "w") as f:
    json.dump(teams_db, f, indent=2)

print("Teams successfully registered / updated.")
