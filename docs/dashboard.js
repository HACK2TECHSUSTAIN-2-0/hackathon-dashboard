const DATA_PATH = "data";

/* ---------- UTILS ---------- */
async function loadJSON(path) {
  const res = await fetch(`${path}?ts=${Date.now()}`);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json();
}

function formatTimeAMPM(utc) {
  if (!utc || utc === "-") return "-";

  const d = new Date(utc);
  return d.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
    timeZone: "Asia/Kolkata"
  });
}

/* ---------- LEADERBOARD ---------- */
async function renderLeaderboard() {
  const data = await loadJSON(`${DATA_PATH}/compliance.json`);

  // Convert object → array while preserving team data
  const rows = Object.entries(data).map(([teamId, t]) => ({
    teamId,
    teamName: t.team_name,
    compliance: t.compliance_percent,
    commits: t.total_valid_commits,
    lastCommit: t.last_valid_commit_time,
    missed: t.missed_windows.length
  }));

  // Sort: Compliance ↓ → Commits ↓ → Team Name ↑
  rows.sort((a, b) =>
    b.compliance - a.compliance ||
    b.commits - a.commits ||
    a.teamName.localeCompare(b.teamName)
  );

  let html = `
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Team Name</th>
          <th>Compliance %</th>
          <th>Valid Commits</th>
          <th>Last Commit Time</th>
          <th>Missed Windows</th>
        </tr>
      </thead>
      <tbody>
  `;

  rows.forEach((r, i) => {
    const medal = i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : "";

    html += `
      <tr class="${i < 3 ? "top-rank" : ""}">
        <td>${medal} ${i + 1}</td>
        <td>${r.teamName}</td>
        <td>${r.compliance.toFixed(1)}</td>
        <td>${r.commits}</td>
        <td>${formatTimeAMPM(r.lastCommit)}</td>
        <td>${r.missed}</td>
      </tr>
    `;
  });

  html += "</tbody></table>";

  document.getElementById("leaderboard").innerHTML = html;
  document.getElementById("totalTeams").textContent = rows.length;
}

/* ---------- PENALTIES ---------- */
async function renderPenalties() {
  const penalties = await loadJSON(`${DATA_PATH}/penalties.json`);
  const compliance = await loadJSON(`${DATA_PATH}/compliance.json`);

  let ok = 0, warning = 0, review = 0;

  let html = `
    <table>
      <thead>
        <tr>
          <th>Team</th>
          <th>Status</th>
          <th>Missed Windows</th>
          <th>Note</th>
        </tr>
      </thead>
      <tbody>
  `;

  Object.entries(penalties).forEach(([teamId, p]) => {
    const level = p.penalty_level.toLowerCase();
    const teamName = compliance[teamId]?.team_name || teamId;

    if (level === "ok") ok++;
    else if (level === "warning") warning++;
    else review++; // penalized + review

    html += `
      <tr>
        <td>${teamName}</td>
        <td><span class="badge ${level}">${p.penalty_level}</span></td>
        <td>${p.missed_windows}</td>
        <td>${p.note}</td>
      </tr>
    `;
  });

  html += "</tbody></table>";

  document.getElementById("penalties").innerHTML = html;
  document.getElementById("compliantTeams").textContent = ok;
  document.getElementById("warningTeams").textContent = warning;
  document.getElementById("reviewTeams").textContent = review;
}


/* ---------- INIT ---------- */
renderLeaderboard();
renderPenalties();

setInterval(() => {
  renderLeaderboard();
  renderPenalties();
}, 60000);
