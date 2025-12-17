const DATA_PATH = "data";

/* ---------- UTILS ---------- */
async function loadJSON(path) {
  const res = await fetch(`${path}?ts=${Date.now()}`);
  return res.json();
}

function animateValue(id, end) {
  let start = 0;
  const el = document.getElementById(id);
  const step = Math.max(1, Math.floor(end / 40));

  const timer = setInterval(() => {
    start += step;
    if (start >= end) {
      el.textContent = end;
      clearInterval(timer);
    } else {
      el.textContent = start;
    }
  }, 20);
}

/* ---------- LEADERBOARD ---------- */
async function renderLeaderboard() {
  const data = await loadJSON(`${DATA_PATH}/compliance.json`);
  const rows = Object.values(data);

  rows.sort((a, b) =>
    b.compliance_percent - a.compliance_percent ||
    b.total_valid_commits - a.total_valid_commits ||
    a.team_name.localeCompare(b.team_name)
  );

  let html = `
    <table>
      <tr>
        <th>Rank</th>
        <th>Team</th>
        <th>Compliance %</th>
        <th>Commits</th>
        <th>Last Commit</th>
        <th>Missed</th>
      </tr>
  `;

  rows.forEach((t, i) => {
    const medal = i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : "";
    html += `
      <tr class="${i < 3 ? "top-rank" : ""}">
        <td>${medal} ${i + 1}</td>
        <td>${t.team_name}</td>
        <td>${t.compliance_percent.toFixed(1)}</td>
        <td>${t.total_valid_commits}</td>
        <td>${t.last_valid_commit_time || "-"}</td>
        <td>${t.missed_windows.length}</td>
      </tr>
    `;
  });

  html += "</table>";
  document.getElementById("leaderboard").innerHTML = html;

  animateValue("totalTeams", rows.length);
}

/* ---------- PENALTIES ---------- */
async function renderPenalties() {
  const penalties = await loadJSON(`${DATA_PATH}/penalties.json`);
  const teams = await loadJSON(`${DATA_PATH}/teams.json`);

  let ok = 0, warning = 0, review = 0;

  let html = `
    <table>
      <tr>
        <th>Team</th>
        <th>Status</th>
        <th>Missed Windows</th>
      </tr>
  `;

  Object.entries(penalties).forEach(([id, p]) => {
    const level = p.penalty_level.toLowerCase();
    if (level === "ok") ok++;
    else if (level === "warning") warning++;
    else review++;

    html += `
      <tr>
        <td>${teams[id]?.team_name || id}</td>
        <td><span class="badge ${level}">${p.penalty_level}</span></td>
        <td>${p.missed_windows}</td>
      </tr>
    `;
  });

  html += "</table>";
  document.getElementById("penalties").innerHTML = html;

  animateValue("compliantTeams", ok);
  animateValue("warningTeams", warning);
  animateValue("reviewTeams", review);
}

/* ---------- INIT ---------- */
renderLeaderboard();
renderPenalties();
setInterval(() => {
  renderLeaderboard();
  renderPenalties();
}, 60000);
