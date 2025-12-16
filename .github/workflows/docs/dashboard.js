async function loadJSON(path) {
  const res = await fetch(path);
  return res.json();
}

async function renderLeaderboard() {
  const res = await fetch("../leaderboard.md");
  const text = await res.text();

  const lines = text.split("\n").filter(l => l.startsWith("|") && !l.includes("----"));
  let html = "<table><tr><th>Rank</th><th>Team</th><th>Compliance %</th><th>Commits</th><th>Missed</th></tr>";

  lines.slice(1).forEach(line => {
    const cols = line.split("|").map(c => c.trim());
    html += `<tr>
      <td>${cols[1]}</td>
      <td>${cols[2]}</td>
      <td>${cols[3]}</td>
      <td>${cols[4]}</td>
      <td>${cols[5]}</td>
    </tr>`;
  });

  html += "</table>";
  document.getElementById("leaderboard").innerHTML = html;
}

async function renderPenalties() {
  const penalties = await loadJSON("../stats/penalties.json");

  let html = "<table><tr><th>Team</th><th>Status</th><th>Missed Windows</th></tr>";

  Object.entries(penalties).forEach(([repo, data]) => {
    const team = repo.split("-")[0].toUpperCase();
    const level = data.penalty_level.toLowerCase();

    html += `<tr>
      <td>${team}</td>
      <td class="${level}">${data.penalty_level}</td>
      <td>${data.missed_windows}</td>
    </tr>`;
  });

  html += "</table>";
  document.getElementById("penalties").innerHTML = html;
}

renderLeaderboard();
renderPenalties();
