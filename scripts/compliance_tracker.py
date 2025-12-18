import requests
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
import os

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "hackathonConfig.json"
TEAMS_FILE = BASE_DIR / "docs" / "data" / "teams.json"
OUTPUT_FILE = BASE_DIR / "docs" / "data" / "compliance.json"

# -----------------------------
# LOAD CONFIG
# -----------------------------
with open(CONFIG_FILE) as f:
    CONFIG = json.load(f)

ORG = CONFIG["organization"]
WINDOW_HOURS = CONFIG["window_hours"]

HACKATHON_START = datetime.strptime(
    CONFIG["hackathon_start_utc"],
    "%Y-%m-%dT%H:%M:%SZ"
).replace(tzinfo=timezone.utc)

TEAM_PATTERN = re.compile(r"\[T\d{3}\]")

# -----------------------------
# AUTH
# -----------------------------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN not set")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# -----------------------------
# HELPERS
# -----------------------------
def parse_time(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )

def get_window_number(commit_time: datetime) -> int | None:
    delta_hours = (commit_time - HACKATHON_START).total_seconds() / 3600
    if delta_hours < 0:
        return None
    return math.floor(delta_hours / WINDOW_HOURS) + 1

def total_windows_elapsed() -> int:
    now = datetime.now(timezone.utc)
    elapsed_hours = (now - HACKATHON_START).total_seconds() / 3600
    return max(0, math.ceil(elapsed_hours / WINDOW_HOURS))

def fetch_commits(repo: str):
    url = f"https://api.github.com/repos/{ORG}/{repo}/commits"
    response = requests.get(url, headers=HEADERS)

    if response.status_code in (404, 409):
        # 404 → repo missing
        # 409 → repo exists but empty
        return []

    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API error for repo '{repo}': "
            f"{response.status_code} {response.text}"
        )

    data = response.json()
    return data if isinstance(data, list) else []



# -----------------------------
# LOAD TEAMS (SOURCE OF TRUTH)
# -----------------------------
with open(TEAMS_FILE) as f:
    teams = json.load(f)

# -----------------------------
# INITIALIZE RESULTS (KEY FIX)
# -----------------------------
results = {}

for team_id, info in teams.items():
    results[team_id] = {
        "team_name": info["team_name"],          # exact Excel name
        "repo": info["repo"],
        "total_valid_commits": 0,
        "windows_covered": [],
        "missed_windows": [],
        "total_windows": 0,
        "compliance_percent": 0.0,
        "last_valid_commit_time": "-"
    }

# -----------------------------
# PROCESS COMMITS
# -----------------------------
for team_id, info in teams.items():
    repo = info["repo"]
    commits = fetch_commits(repo)

    windows_covered = set()
    valid_commit_count = 0
    last_commit_time = None

    for c in commits:
        msg = c["commit"]["message"]

        if not TEAM_PATTERN.search(msg):
            continue

        commit_time = parse_time(c["commit"]["author"]["date"])
        if commit_time < HACKATHON_START:
            continue

        window = get_window_number(commit_time)
        if window:
            windows_covered.add(window)
            valid_commit_count += 1
            if not last_commit_time or commit_time > last_commit_time:
                last_commit_time = commit_time

    total_windows = total_windows_elapsed()
    missed_windows = sorted(
        set(range(1, total_windows + 1)) - windows_covered
    )

    compliance = (
        round((len(windows_covered) / total_windows) * 100, 2)
        if total_windows > 0 else 0
    )

    results[team_id].update({
        "total_valid_commits": valid_commit_count,
        "windows_covered": sorted(windows_covered),
        "missed_windows": missed_windows,
        "total_windows": total_windows,
        "compliance_percent": compliance,
        "last_valid_commit_time": (
            last_commit_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            if last_commit_time else "-"
        )
    })

# -----------------------------
# SAVE OUTPUT
# -----------------------------
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print("Compliance stats updated successfully")
