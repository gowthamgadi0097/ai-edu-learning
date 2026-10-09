const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
async function api(url, body) {
  const res = await fetch(url, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  if (res.status === 401) { location.href = "/login"; return {}; }
  return res.json();
}

// ---- tabs ----
document.querySelectorAll(".tabs button").forEach((b) =>
  b.addEventListener("click", () => {
    document.querySelectorAll(".tabs button").forEach((x) => x.classList.toggle("active", x === b));
    ["chat", "quiz", "resources", "progress"].forEach((id) => $(id).classList.toggle("hidden", id !== b.dataset.tab));
    if (b.dataset.tab === "resources") loadResources();
    if (b.dataset.tab === "progress") loadProgress();
  })
);

// ---- chat ----
function addMsg(text, who) {
  const d = document.createElement("div");
  d.className = "msg " + who;
  d.textContent = text;
  $("log").appendChild(d);
  $("log").scrollTop = $("log").scrollHeight;
  return d;
}
async function send() {
  const text = $("msg").value.trim();
  if (!text) return;
  $("msg").value = "";
  addMsg(text, "user");
  const wait = addMsg("Thinking...", "bot");
  $("send").disabled = true;
  try {
    const r = await api("/api/chat", { message: text });
    wait.textContent = r.answer || r.error || "Something went wrong.";
  } catch (e) {
    wait.textContent = "Network error. Please try again.";
  }
  $("send").disabled = false;
}
$("send").addEventListener("click", send);
$("msg").addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
api("/api/chat/history").then((r) => (r.history || []).forEach((h) => { addMsg(h.question, "user"); addMsg(h.answer, "bot"); }));

// ---- quiz ----
let quiz = null;
$("gen").addEventListener("click", async () => {
  $("gen").disabled = true;
  $("quizBox").textContent = "Generating...";
  const r = await api("/api/quiz/generate", { topic: $("topic").value, n: 5 });
  $("gen").disabled = false;
  if (r.error) { $("quizBox").textContent = r.error; return; }
  quiz = r;
  $("quizBox").innerHTML =
    `<p class="muted">Source: ${r.source === "ai" ? "AI-generated (check answers with your teacher)" : "teacher-approved question bank"}</p>` +
    r.questions.map((q, i) =>
      `<div class="q"><strong>${i + 1}. ${esc(q.q)}</strong>` +
      q.options.map((o, j) => `<label class="opt"><input type="radio" name="q${i}" value="${j}">${esc(o)}</label>`).join("") +
      `<div class="fb" id="fb${i}"></div></div>`).join("") +
    `<button id="submitQuiz">Submit answers</button><p id="scoreLine"></p>`;
  $("submitQuiz").addEventListener("click", submitQuiz);
});
async function submitQuiz() {
  const answers = quiz.questions.map((_, i) => {
    const c = document.querySelector(`input[name=q${i}]:checked`);
    return c ? Number(c.value) : null;
  });
  const r = await api("/api/quiz/submit", { answers });
  if (r.error) { $("scoreLine").textContent = r.error; return; }
  r.details.forEach((d, i) => {
    $("fb" + i).className = "fb " + (d.correct ? "good" : "bad");
    $("fb" + i).textContent = (d.correct ? "Correct. " : "Incorrect. Right answer: " + d.right_answer + ". ") + d.explain;
  });
  $("scoreLine").innerHTML = `<strong>Score: ${r.score} / ${r.total}</strong>`;
  $("submitQuiz").disabled = true;
}

// ---- resources ----
async function loadResources() {
  const r = await api("/api/recommendations");
  const list = r.recommendations || [];
  $("recList").innerHTML = list.length
    ? list.map((x) => `<p><span class="pill">${esc(x.topic)}</span> <a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.title)}</a><br><span class="muted">${esc(x.why)} Why suggested: ${esc(x.reason)}</span></p>`).join("")
    : '<p class="muted">Great work: no weak topics right now.</p>';
}

// ---- progress ----
async function loadProgress() {
  const r = await api("/api/progress");
  const stats = Object.entries(r.stats || {});
  $("progBox").innerHTML =
    `<p>Questions asked to the assistant: <strong>${r.questions_asked}</strong></p>` +
    (stats.length ? stats.map(([t, s]) => `<p>${esc(t)}: ${s.pct}% <span class="muted">(${s.attempts} quizzes)</span></p><div class="bar"><div style="width:${s.pct}%"></div></div>`).join("") : '<p class="muted">Take a quiz to see your progress.</p>') +
    (r.recent && r.recent.length ? "<h4>Recent quizzes</h4><table><tr><th>Topic</th><th>Score</th><th>Date (UTC)</th></tr>" +
      r.recent.map((q) => `<tr><td>${esc(q.topic)}</td><td>${q.score}/${q.total}</td><td>${esc(q.created_at)}</td></tr>`).join("") + "</table>" : "");
}
