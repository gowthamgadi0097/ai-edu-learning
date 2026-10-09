"""AI-Powered Personalized Learning and Student Assistance System (Flask backend)."""
import json
import os
import random
import sqlite3
from datetime import datetime
from functools import wraps

import requests
from dotenv import load_dotenv
from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from data import KNOWLEDGE_BASE, QUESTION_BANK, RESOURCES, TOPICS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "learning.db"))
TEACHER_CODE = os.environ.get("TEACHER_CODE", "TEACH123")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")  # free tier available via Google AI Studio
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
if ANTHROPIC_KEY:
    PROVIDER, API_KEY, DEFAULT_MODEL = "anthropic", ANTHROPIC_KEY, "claude-sonnet-5-5"
elif GEMINI_KEY:
    PROVIDER, API_KEY, DEFAULT_MODEL = "gemini", GEMINI_KEY, "gemini-3.8-flash"
else:
    PROVIDER, API_KEY, DEFAULT_MODEL = None, "", ""
AI_ON = bool(API_KEY)
AI_MODEL = os.environ.get("AI_MODEL") or DEFAULT_MODEL

SYSTEM_PROMPT = (
    "You are a friendly AI study assistant for engineering students. Explain concepts clearly with short "
    "examples. If you are not sure about something, say so instead of guessing. Encourage students to "
    "verify important facts with their teacher or textbook. Keep answers under 200 words."
)


# ---------- database ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS chats(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS quiz_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    db.commit()
    db.close()


def now():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


# ---------- auth ----------
def login_required(role=None):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if "user_id" not in session:
                if request.path.startswith("/api/"):
                    return jsonify(error="Please log in."), 401
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                if request.path.startswith("/api/"):
                    return jsonify(error="Not allowed."), 403
                return redirect(url_for("home"))
            return fn(*a, **kw)
        return wrapper
    return deco


@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("teacher" if session["role"] == "teacher" else "dashboard"))


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "student")
        code = request.form.get("teacher_code", "")
        if not name or "@" not in email or len(password) < 6:
            error = "Enter a name, a valid email and a password of at least 6 characters."
        elif role == "teacher" and code != TEACHER_CODE:
            error = "Invalid teacher access code."
        else:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO users(name,email,password_hash,role,created_at) VALUES(?,?,?,?,?)",
                    (name, email, generate_password_hash(password), "teacher" if role == "teacher" else "student", now()),
                )
                db.commit()
                return redirect(url_for("login", registered=1))
            except sqlite3.IntegrityError:
                error = "That email is already registered."
    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.update(user_id=user["id"], name=user["name"], role=user["role"])
            return redirect(url_for("home"))
        error = "Incorrect email or password."
    return render_template("login.html", error=error, registered=request.args.get("registered"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- pages ----------
@app.route("/dashboard")
@login_required("student")
def dashboard():
    return render_template("dashboard.html", name=session["name"], topics=TOPICS, ai_on=AI_ON)


@app.route("/teacher")
@login_required("teacher")
def teacher():
    return render_template("teacher.html", name=session["name"])


# ---------- AI helpers ----------
def call_ai(messages, max_tokens=700, system=SYSTEM_PROMPT):
    """Call the configured AI provider from the server (key never reaches the browser)."""
    if PROVIDER == "gemini":
        r = requests.post(
            GEMINI_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": AI_MODEL, "max_tokens": max_tokens,
                  "messages": [{"role": "system", "content": system}] + messages},
            timeout=40,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"] or ""
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": AI_MODEL, "max_tokens": max_tokens, "system": system, "messages": messages},
        timeout=40,
    )
    r.raise_for_status()
    return "".join(b.get("text", "") for b in r.json().get("content", []))


def offline_answer(question):
    q = question.lower()
    hits = [text for key, text in KNOWLEDGE_BASE.items() if key in q]
    if hits:
        return "\n\n".join(hits[:2]) + "\n\n(Offline mode: answers come from a small built-in knowledge base.)"
    return ("I don't have a verified answer for that in offline mode. Try keywords like stack, queue, binary search, "
            "normalization, join, overfitting or gradient descent, or ask your teacher. "
            "(Add an API key to enable full AI answers.)")


# ---------- API: chat ----------
@app.route("/api/chat", methods=["POST"])
@login_required("student")
def api_chat():
    question = (request.json or {}).get("message", "").strip()
    if not question:
        return jsonify(error="Type a question first."), 400
    if len(question) > 1000:
        return jsonify(error="Question is too long (max 1000 characters)."), 400
    db = get_db()
    history = db.execute(
        "SELECT question, answer FROM chats WHERE user_id=? ORDER BY id DESC LIMIT 4", (session["user_id"],)
    ).fetchall()[::-1]
    mode = "offline"
    try:
        if AI_ON:
            msgs = []
            for h in history:
                msgs += [{"role": "user", "content": h["question"]}, {"role": "assistant", "content": h["answer"]}]
            msgs.append({"role": "user", "content": question})
            answer, mode = call_ai(msgs), "ai"
        else:
            answer = offline_answer(question)
    except Exception:
        answer = offline_answer(question) + "\n\n(The AI service is unreachable right now.)"
    db.execute("INSERT INTO chats(user_id,question,answer,created_at) VALUES(?,?,?,?)",
               (session["user_id"], question, answer, now()))
    db.commit()
    return jsonify(answer=answer, mode=mode)


@app.route("/api/chat/history")
@login_required("student")
def api_history():
    rows = get_db().execute(
        "SELECT question, answer, created_at FROM chats WHERE user_id=? ORDER BY id DESC LIMIT 20",
        (session["user_id"],),
    ).fetchall()
    return jsonify(history=[dict(r) for r in rows][::-1])


# ---------- API: quiz ----------
def ai_quiz(topic, n):
    prompt = (
        f"Create {n} multiple-choice questions on {topic} for engineering students. Reply with ONLY a JSON array. "
        'Each item: {"q": str, "options": [4 strings], "answer": index 0-3, "explain": str}.'
    )
    text = call_ai([{"role": "user", "content": prompt}], max_tokens=1800, system="You write accurate quiz questions.")
    start, end = text.find("["), text.rfind("]")
    items = json.loads(text[start:end + 1])
    clean = []
    for it in items:  # validate before use
        if (isinstance(it.get("q"), str) and isinstance(it.get("options"), list) and len(it["options"]) == 4
                and isinstance(it.get("answer"), int) and 0 <= it["answer"] < 4):
            clean.append({"q": it["q"], "options": [str(o) for o in it["options"]],
                          "answer": it["answer"], "explain": str(it.get("explain", ""))})
    if not clean:
        raise ValueError("no valid questions")
    return clean[:n]


@app.route("/api/quiz/generate", methods=["POST"])
@login_required("student")
def api_quiz_generate():
    body = request.json or {}
    topic = body.get("topic")
    if topic not in TOPICS:
        return jsonify(error="Choose a valid topic."), 400
    n = max(3, min(int(body.get("n", 5)), 5))
    source = "bank"
    questions = None
    if AI_ON:
        try:
            questions, source = ai_quiz(topic, n), "ai"
        except Exception:
            questions = None
    if questions is None:
        questions = random.sample(QUESTION_BANK[topic], min(n, len(QUESTION_BANK[topic])))
    session["quiz"] = {"topic": topic, "questions": questions}
    public = [{"q": q["q"], "options": q["options"]} for q in questions]
    return jsonify(topic=topic, questions=public, source=source)


@app.route("/api/quiz/submit", methods=["POST"])
@login_required("student")
def api_quiz_submit():
    quiz = session.get("quiz")
    if not quiz:
        return jsonify(error="No active quiz. Generate one first."), 400
    answers = (request.json or {}).get("answers", [])
    details, score = [], 0
    for i, q in enumerate(quiz["questions"]):
        chosen = answers[i] if i < len(answers) else None
        ok = chosen == q["answer"]
        score += ok
        details.append({"correct": ok, "right_answer": q["options"][q["answer"]], "explain": q["explain"], "chosen": chosen})
    total = len(quiz["questions"])
    db = get_db()
    db.execute("INSERT INTO quiz_results(user_id,topic,score,total,created_at) VALUES(?,?,?,?,?)",
               (session["user_id"], quiz["topic"], score, total, now()))
    db.commit()
    session.pop("quiz", None)
    return jsonify(score=score, total=total, details=details)


# ---------- API: progress & recommendations ----------
def topic_stats(user_id):
    rows = get_db().execute(
        "SELECT topic, SUM(score) s, SUM(total) t, COUNT(*) attempts FROM quiz_results WHERE user_id=? GROUP BY topic",
        (user_id,),
    ).fetchall()
    return {r["topic"]: {"pct": round(100 * r["s"] / r["t"]) if r["t"] else 0, "attempts": r["attempts"]} for r in rows}


@app.route("/api/progress")
@login_required("student")
def api_progress():
    db = get_db()
    recent = db.execute(
        "SELECT topic, score, total, created_at FROM quiz_results WHERE user_id=? ORDER BY id DESC LIMIT 10",
        (session["user_id"],),
    ).fetchall()
    chats = db.execute("SELECT COUNT(*) c FROM chats WHERE user_id=?", (session["user_id"],)).fetchone()["c"]
    return jsonify(stats=topic_stats(session["user_id"]), recent=[dict(r) for r in recent], questions_asked=chats)


@app.route("/api/recommendations")
@login_required("student")
def api_recommendations():
    stats = topic_stats(session["user_id"])
    recs = []
    for topic in TOPICS:
        st = stats.get(topic)
        if st is None:
            reason = "You haven't taken a quiz on this topic yet."
        elif st["pct"] < 70:
            reason = f"Your average quiz score here is {st['pct']}%, below 70%."
        else:
            continue
        for res in RESOURCES[topic]:
            recs.append({"topic": topic, "reason": reason, **res})
    return jsonify(recommendations=recs)


# ---------- API: teacher ----------
@app.route("/api/teacher/overview")
@login_required("teacher")
def api_teacher_overview():
    db = get_db()
    students = db.execute(
        """SELECT u.id, u.name, u.email,
                  (SELECT COUNT(*) FROM chats c WHERE c.user_id=u.id) AS questions,
                  (SELECT COUNT(*) FROM quiz_results q WHERE q.user_id=u.id) AS quizzes,
                  (SELECT ROUND(100.0*SUM(score)/NULLIF(SUM(total),0)) FROM quiz_results q WHERE q.user_id=u.id) AS avg_pct
           FROM users u WHERE u.role='student' ORDER BY u.name"""
    ).fetchall()
    topics = db.execute(
        "SELECT topic, ROUND(100.0*SUM(score)/SUM(total)) AS avg_pct, COUNT(*) AS attempts "
        "FROM quiz_results GROUP BY topic ORDER BY topic"
    ).fetchall()
    return jsonify(students=[dict(s) for s in students], topics=[dict(t) for t in topics])


if __name__ == "__main__":
    init_db()
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=int(os.environ.get("PORT", 5000)))
else:
    init_db()
