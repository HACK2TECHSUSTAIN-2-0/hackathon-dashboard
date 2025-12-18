const DATA_PATH = "data";
const REFRESH_INTERVAL = 60000; // 60 seconds

/* ---------- UTILS ---------- */
async function loadJSON(path) {
  try {
    const res = await fetch(`${path}? ts=${Date.now()}`);
    if (!res.ok) throw new Error(`Failed to load ${path}`);
    return res.json();
  } catch (error) {
    console.error(`Error loading ${path}:`, error);
    return null;
  }
}

function formatTimeAMPM(utc) {
  if (!utc || utc === "-") return "-";

  try {
    const d = new Date(utc);
    return d.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
      timeZone: "Asia/Kolkata"
    });
  } catch (error) {
    return "-";
  }
}

function showLoading(elementId) {
  const el = document.getElementById(elementId);
  if (el) {
    el.innerHTML = '<div style="text-align: center; padding: 20px; color: var(--text-secondary);"><i class="fas fa-spinner fa-spin" style="font-size: 24px;"></i><p style="margin-top: 10px;">Loading data... </p></div>';
  }
}

function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--danger);"><i class="fas fa-exclamation-triangle" style="font-size: 24px;"></i><p style="margin-top: 10px;">${message}</p></div>`;
  }
}

/* ---------- LEADERBOARD ---------- */
async function renderLeaderboard() {
  showLoading('leaderboard');
  
  const data = await loadJSON(`${DATA_PATH}/compliance.json`);
  
  if (!data) {
    showError('leaderboard', 'Failed to load leaderboard data');
    return;
  }

  // Convert object → array while preserving team data
  const rows = Object.entries(data).map(([teamId, t]) => ({
    teamId,
    teamName: t.team_name,
    compliance: t.compliance_percent,
    commits: t.total_valid_commits,
    lastCommit: t.last_valid_commit_time,
    missed:  t.missed_windows.length
  }));

  // Sort: Compliance ↓ → Commits ↓ → Team Name ↑
  rows.sort((a, b) =>
    b.compliance - a. compliance ||
    b.commits - a.commits ||
    a. teamName.localeCompare(b.teamName)
  );

  let html = `
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Team Name</th>
          <th>Compliance %</th>
          <th>Valid Commits</th>
          <th>Last Activity</th>
          <th>Missed Windows</th>
        </tr>
      </thead>
      <tbody>
  `;

  rows.forEach((r, i) => {
    const medal = i === 0 ? "🥇" : i === 1 ? "🥈" :  i === 2 ? "🥉" : "";
    const rankDisplay = medal ?  medal :  `#${i + 1}`;

    html += `
      <tr class="${i < 3 ? "top-rank" : ""}">
        <td><strong>${rankDisplay}</strong></td>
        <td><strong>${r.teamName}</strong></td>
        <td><strong>${r.compliance.toFixed(1)}%</strong></td>
        <td>${r.commits}</td>
        <td>${formatTimeAMPM(r.lastCommit)}</td>
        <td>${r.missed > 0 ? `<span style="color: var(--warning);">${r.missed}</span>` : r.missed}</td>
      </tr>
    `;
  });

  html += "</tbody></table>";

  document.getElementById("leaderboard").innerHTML = html;
  document.getElementById("totalTeams").textContent = rows.length;
}

/* ---------- PENALTIES ---------- */
async function renderPenalties() {
  showLoading('penalties');
  
  const penalties = await loadJSON(`${DATA_PATH}/penalties.json`);
  const compliance = await loadJSON(`${DATA_PATH}/compliance.json`);

  if (!penalties || !compliance) {
    showError('penalties', 'Failed to load compliance data');
    return;
  }

  let ok = 0, warning = 0, review = 0;

  let html = `
    <table>
      <thead>
        <tr>
          <th>Team Name</th>
          <th>Status</th>
          <th>Missed Windows</th>
          <th>Notes</th>
        </tr>
      </thead>
      <tbody>
  `;

  Object.entries(penalties).forEach(([teamId, p]) => {
    const level = p.penalty_level. toLowerCase();
    const teamName = compliance[teamId]?.team_name || teamId;

    if (level === "ok") ok++;
    else if (level === "warning") warning++;
    else if (level === "review") review++;

    const badgeClass = level === "ok" ? "ok" : level === "warning" ? "warning" : "review";
    const icon = level === "ok" ? "fa-check-circle" : level === "warning" ? "fa-exclamation-triangle" : "fa-times-circle";

    html += `
      <tr>
        <td><strong>${teamName}</strong></td>
        <td><span class="badge ${badgeClass}"><i class="fas ${icon}"></i> ${p.penalty_level}</span></td>
        <td>${p. missed_windows}</td>
        <td style="color: var(--text-secondary);">${p.note}</td>
      </tr>
    `;
  });

  html += "</tbody></table>";

  document.getElementById("penalties").innerHTML = html;
  document. getElementById("compliantTeams").textContent = ok;
  document.getElementById("warningTeams").textContent = warning;
  document.getElementById("reviewTeams").textContent = review;
}

/* ---------- INIT & REFRESH ---------- */
async function refreshDashboard() {
  await Promise.all([
    renderLeaderboard(),
    renderPenalties()
  ]);
  console.log(`Dashboard refreshed at ${new Date().toLocaleTimeString()}`);
}

// Initial load
refreshDashboard();

// Auto-refresh
setInterval(refreshDashboard, REFRESH_INTERVAL);
