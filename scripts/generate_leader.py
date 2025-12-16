import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATS_FILE = BASE_DIR / "stats" / "compliance.json"
LEADERBOARD_FILE = BASE_DIR / "leaderboard.md"

with open(STATS_FILE) as f:
    data = json.load(f)

rows = []

for repo, stats in data.items():
    team_id = repo.split("-")[0].upper()  # t001 → T001

    rows.append({
        "team": team_id,
        "compliance": stats["compliance_percent"],
        "commits": stats["total_valid_commits"],
        "missed": len(stats["missed_windows"])
    })

# Sort: compliance ↓, commits ↓, team ↑
rows.sort(
    key=lambda x: (-x["compliance"], -x["commits"], x["team"])
)

# Generate Markdown
lines = []
lines.append("# 🏆 Hackathon Live Leaderboard\n")
lines.append("| Rank | Team | Compliance % | Valid Commits | Missed Windows |")
lines.append("|----|----|----|----|----|")

for i, r in enumerate(rows, start=1):
    lines.append(
        f"| {i} | {r['team']} | {r['compliance']} | {r['commits']} | {r['missed']} |"
    )

LEADERBOARD_FILE.write_text("\n".join(lines))

print("Leaderboard generated successfully.")
