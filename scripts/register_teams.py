import json, argparse, os
from excel_reader import read_excel
from utils import slugify
from github_api import gh

ORG = "HACK2TECHSUSTAIN-2-0"
BASE_HEADERS = {
    "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github+json"
}

parser = argparse.ArgumentParser()
parser.add_argument("--excel", required=True)
args = parser.parse_args()

rows = read_excel(args.excel)

teams_db = {}

for r in rows:
    team_id = r["TeamID"]
    team_name = r["Team Name"]
    emails = [e.strip() for e in r["GitHub Emails"].split(",")]
    ps_id = r.get("PS ID")
    ps = r.get("PS")

    repo = slugify(team_name)
    team_slug = f"team-{team_id.lower()}"

    # Create team (safe)
    gh(BASE_HEADERS, "POST", f"/orgs/{ORG}/teams", json={
        "name": team_slug,
        "privacy": "secret"
    })

    # Create repo (safe)
    gh(BASE_HEADERS, "POST", f"/orgs/{ORG}/repos", json={
        "name": repo,
        "private": True,
        "description": f"TeamID: {team_id} | PS: {ps or 'Not assigned'}"
    })

    # Permission
    perm = "push" if ps_id else "pull"
    gh(BASE_HEADERS, "PUT",
       f"/orgs/{ORG}/teams/{team_slug}/repos/{ORG}/{repo}",
       json={"permission": perm})

    teams_db[team_id] = {
        "team_name": team_name,
        "repo": repo,
        "members": emails,
        "ps_id": ps_id,
        "ps": ps,
        "access": perm
    }

with open("data/teams.json", "w") as f:
    json.dump(teams_db, f, indent=2)
