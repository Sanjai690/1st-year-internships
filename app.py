
import csv
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DATA_FILE = Path(__file__).with_name("careers.csv")
WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z\-+.#]*")
GREETING_WORDS = {"hi", "hello", "hey", "good", "morning", "afternoon", "evening"}
EXIT_WORDS = {"bye", "exit", "quit", "thanks", "thank", "goodbye"}


def load_career_data(file_path: Path):
    """Load CSV and keep frequency counts per skill to enable ranking."""
    skill_to_career_counts = defaultdict(Counter)

    if not file_path.exists():
        app.logger.warning("Data file not found: %s", file_path)
        return skill_to_career_counts

    with file_path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            skill = (row.get("skill") or "").strip().lower()
            career = (row.get("career") or "").strip()
            if skill and career:
                skill_to_career_counts[skill][career] += 1

    return skill_to_career_counts


def tokenize_user_input(user_input: str):
    return [token.lower() for token in WORD_RE.findall(user_input)]


def detect_intent(tokens):
    token_set = set(tokens)
    if token_set & GREETING_WORDS:
        return "greeting"
    if token_set & EXIT_WORDS:
        return "exit"
    return "query"


def get_recommendations(tokens, skill_to_career_counts, limit=5):
    matched_skills = []
    combined_scores = Counter()

    for token in tokens:
        if token in skill_to_career_counts:
            matched_skills.append(token)
            combined_scores.update(skill_to_career_counts[token])

    top_careers = [career for career, _ in combined_scores.most_common(limit)]
    return matched_skills, top_careers


def build_chat_response(user_input: str, skill_to_career_counts):
    cleaned_input = (user_input or "").strip()
    if not cleaned_input:
        return {
            "reply": "Please enter a skill or interest so I can suggest careers.",
            "matched_skills": [],
            "recommendations": [],
        }

    tokens = tokenize_user_input(cleaned_input)
    intent = detect_intent(tokens)

    if intent == "greeting":
        return {
            "reply": "Hello. Share one or more skills or interests, and I will suggest career paths.",
            "matched_skills": [],
            "recommendations": [],
        }

    if intent == "exit":
        return {
            "reply": "You're welcome. Wishing you success in your career journey.",
            "matched_skills": [],
            "recommendations": [],
        }

    matched_skills, recommendations = get_recommendations(tokens, skill_to_career_counts)

    if recommendations:
        skill_preview = ", ".join(sorted(set(matched_skills)))
        return {
            "reply": f"Top career matches based on: {skill_preview}.",
            "matched_skills": sorted(set(matched_skills)),
            "recommendations": recommendations,
        }

    return {
        "reply": "No direct match found. Try keywords like data, design, coding, leadership, teaching, finance, or marketing.",
        "matched_skills": [],
        "recommendations": [],
    }


career_map = load_career_data(DATA_FILE)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "records": sum(sum(c.values()) for c in career_map.values())})


@app.route("/api/chat", methods=["POST"])
def chat_api():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "")
    result = build_chat_response(message, career_map)
    return jsonify(result)


@app.route("/get", methods=["POST"])
def get_response():
    # Backward-compatible endpoint used by the current frontend.
    user_input = request.form.get("msg", "")
    result = build_chat_response(user_input, career_map)

    if result["recommendations"]:
        return result["reply"] + " Suggested roles: " + ", ".join(result["recommendations"])
    return result["reply"]


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=debug)
