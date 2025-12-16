import requests
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
import os

# -----------------------------
# LOAD CONFIG
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "hackathonConfig.json"
OUTPUT_FILE = BASE_DIR / "stats" / "compliance.json"

with open(CONFIG_FILE) as f:
    CONFIG = json.load(f)

ORG = CONFIG["organization"]
REPOS = CONFIG["repositories"]
WINDOW_HOURS = CONFIG["window_hours"]

HACKATHON_START = datetime.strptime(
    CONFIG["hackathon_start_utc"],
    "%Y-%m-%dT%H:%M:%SZ"
).replace(tzinfo=timezone.utc)

TEAM_PATTERN = re.compile(r"\[T\d{3}\]")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# -----------------------------
# HELPERS
# -----------------------------
def parse_time(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def get_window_number(commit_time: datetime) -> int:
    delta_hours = (commit_time - HACKATHON_START).total_seconds() / 3600
    if delta_hours < 0:
        return None
    return math.floor(delta_hours / WINDOW_HOURS) + 1

def total_windows_elapsed() -> int:
    now = datetime.now(timezone.utc)
    elapsed_hours = (now - HACKATHON_START).total_seconds() / 3600
    return max(0, math.ceil(elapsed_hours / WINDOW_HOURS))

# -----------------------------
# MAIN LOGIC
# -----------------------------
results = {}

for repo in REPOS:
    url = f"https://api.github.com/repos/{ORG}/{repo}/commits"
    response = requests.get(url, headers=HEADERS)
    commits = response.json()

    windows_covered = set()
    valid_commit_count = 0

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

    total_windows = total_windows_elapsed()
    missed_windows = sorted(
        set(range(1, total_windows + 1)) - windows_covered
    )

    compliance = (
        round((len(windows_covered) / total_windows) * 100, 2)
        if total_windows > 0 else 0
    )

    results[repo] = {
        "total_valid_commits": valid_commit_count,
        "windows_covered": sorted(list(windows_covered)),
        "missed_windows": missed_windows,
        "total_windows": total_windows,
        "compliance_percent": compliance
    }

# -----------------------------
# SAVE OUTPUT
# -----------------------------
OUTPUT_FILE.parent.mkdir(exist_ok=True)

with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print("Compliance stats updated successfully.")
