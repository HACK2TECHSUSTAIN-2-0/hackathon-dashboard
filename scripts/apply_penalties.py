import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
COMPLIANCE_FILE = BASE_DIR / "docs" / "data" / "compliance.json"
PENALTY_FILE = BASE_DIR / "docs" / "data" / "penalties.json"

with open(COMPLIANCE_FILE) as f:
    compliance = json.load(f)

penalties = {}

for repo, stats in compliance.items():
    missed = len(stats["missed_windows"])

    if missed <= 1:
        level = "OK"
        note = "Compliant"
    elif missed <= 3:
        level = "WARNING"
        note = "Low activity detected"
    elif missed <= 5:
        level = "PENALIZED"
        note = "Multiple activity gaps"
    else:
        level = "REVIEW"
        note = "Severe inactivity – review required"

    penalties[repo] = {
        "missed_windows": missed,
        "penalty_level": level,
        "note": note
    }

PENALTY_FILE.write_text(json.dumps(penalties, indent=2))

print("Penalty assessment completed.")
