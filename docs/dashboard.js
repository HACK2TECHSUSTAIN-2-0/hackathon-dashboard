async function loadJSON(path) {
  const res = await fetch(path);
  return res.json();
}

/* LEADERBOARD */
async function renderLeaderboard() {
  const res = await fetch(`data/leaderboard.md?ts=${Date.now()}`);
  const text = await res.text();

  const rows = text
    .split("\n")
    .filter(l => l.startsWith("|") && !l.includes("----"))
    .slice(1);

  let html = `
    <table>
      <tr>
        <th>Rank</th>
        <th>Team</th>
        <th>Compliance %</th>
        <th>Valid Commits</th>
        <th>Missed Windows</th>
      </tr>
  `;

  rows.forEach(r => {
    const c = r.split("|").map(x => x.trim());
    html += `
      <tr>
        <td>${c[1]}</td>
        <td>${c[2]}</td>
        <td>${c[3]}</td>
        <td>${c[4]}</td>
        <td>${c[5]}</td>
      </tr>
    `;
  });

  html += "</table>";
  document.getElementById("leaderboard").innerHTML = html;
}

/* PENALTIES + SUMMARY */
async function renderPenaltiesAndStats() {
  const penalties = await loadJSON(`data/penalties.json?ts=${Date.now()}`);

  let html = `
    <table>
      <tr>
        <th>Team</th>
        <th>Status</th>
        <th>Missed Windows</th>
      </tr>
  `;

  let total = 0, ok = 0, warning = 0, review = 0;

  Object.entries(penalties).forEach(([repo, data]) => {
    const team = repo.split("-")[0].toUpperCase();
    const level = data.penalty_level.toLowerCase();

    total++;
    if (level === "ok") ok++;
    else if (level === "warning") warning++;
    else review++;

    html += `
      <tr>
        <td>${team}</td>
        <td><span class="badge ${level}">${data.penalty_level}</span></td>
        <td>${data.missed_windows}</td>
      </tr>
    `;
  });

  html += "</table>";
  document.getElementById("penalties").innerHTML = html;

  /* SUMMARY */
  document.getElementById("totalTeams").textContent = total;
  document.getElementById("compliantTeams").textContent = ok;
  document.getElementById("warningTeams").textContent = warning;
  document.getElementById("reviewTeams").textContent = review;
}

/* INIT */
renderLeaderboard();
renderPenaltiesAndStats();
