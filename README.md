# AI-Powered Personalized Learning and Student Assistance System

A Flask web app for an AI for Education college project. It follows the structure in the project guide.

## Features
- **AI chatbot** for academic questions (full AI with an API key; small built-in knowledge base in offline mode)
- **Quiz generator** (AI-generated when a key is set, otherwise from a built-in question bank), graded on the server
- **Study-resource recommendations** based on quiz performance, with the reason shown
- **Progress tracking** (quiz scores and activity per student)
- **Teacher dashboard** (aggregate topic performance and per-student summary)
- Login / registration with hashed passwords; teacher accounts need an access code

## Tech stack
HTML, CSS, JavaScript, Python (Flask), SQLite, Anthropic Messages API (optional).

## Run locally (Windows, VS Code terminal or Git Bash)
```bash
python -m venv venv
source venv/Scripts/activate      # Git Bash on Windows
pip install -r requirements.txt
cp .env.example .env              # then edit .env
python app.py
```
Open http://127.0.0.1:5000

## Configuration (`.env`)
| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask session signing key (set a long random value) |
| `TEACHER_CODE` | Code required to register as a teacher |
| `ANTHROPIC_API_KEY` | Optional. Enables AI answers and AI quizzes. Kept on the server only. |
| `AI_MODEL` | Model name used for the API calls |

## Testing notes
Record your own test cases (input, expected, actual, pass/fail) and take real screenshots for Chapter 5 of your report. AI answers can be wrong, and AI-generated quiz questions should be reviewed.

## Limitations
Small built-in question bank (4 topics), internet needed for AI mode, no email verification, SQLite suited to a prototype only.
