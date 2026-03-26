import random as r
import json
import os
from flask import Flask, render_template, request, session, jsonify, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

# Custom Jinja2 filters
app.jinja_env.filters['enumerate'] = enumerate
app.jinja_env.filters['min'] = min

# ─────────────────────────────────────────────────────────────────
# DATA LOADING  (JSON files expected in same folder as app.py)
# ─────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(__file__)

def load_json(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

Exercises    = load_json("exercises.json")
Explanations = load_json("explanations.json")
Tests        = load_json("testing.json")

# ─────────────────────────────────────────────────────────────────
# VISUALIZATION MAP  (maps integer keys from JSON to static URLs)
# Place your images in  static/images/1.png, 2.png, …
# ─────────────────────────────────────────────────────────────────

Visualization_Map = {
    1:  "images/1.png",
    2:  "images/2.png",
    3:  "images/3.png",
    4:  "images/4.png",
    5:  "images/5.png",
    6:  "images/6.png",
    7:  "images/7.png",
    8:  "images/8.png",
    9:  "images/9.png",
    10: "images/10.png",
    11: "images/11.png",
    12: "images/12.png",
    13: "images/13.png",
    14: "images/14.png",
    15: "images/15.png",
    16: "images/16.png",
    17: "images/17.png",
    18: "images/18.png",
    19: "images/19.png",
    20: "images/20.png",
}

def viz_url(viz_key):
    """Return Flask static URL for a visualization key, or None."""
    if viz_key is None:
        return None
    try:
        key = int(viz_key)
    except (ValueError, TypeError):
        return None
    path = Visualization_Map.get(key)
    if not path:
        return None
    # Return path directly — no filesystem check, Flask serves from static/
    return path 

# ─────────────────────────────────────────────────────────────────
# ASSESSMENT QUESTIONS  (unchanged from MVP)
# ─────────────────────────────────────────────────────────────────

assessment_questions = {
    "func_concept": [
        {"difficulty": 0.2, "step_complexity": 0.2, "qtype": "abstract",
         "question": "Welche Aussage beschreibt eine Funktion korrekt?",
         "choices": ["Jedem x-Wert wird genau ein y-Wert zugeordnet",
                     "Ein x-Wert kann mehrere y-Werte haben",
                     "Jeder y-Wert muss positiv sein",
                     "Eine Funktion ist immer eine Gerade"],
         "correct": 0},
        {"difficulty": 0.3, "step_complexity": 0.4, "qtype": "example",
         "question": "Ein Taxi kostet 4€ Grundgebühr + 2€ pro km. Welche Aussage stimmt?",
         "choices": ["Zu jeder gefahrenen Strecke gehört genau ein Preis",
                     "Eine Strecke kann mehrere Preise haben",
                     "Der Preis ist unabhängig von der Strecke",
                     "Der Preis sinkt mit der Strecke"],
         "correct": 0},
        {"difficulty": 0.5, "step_complexity": 0.5, "qtype": "abstract",
         "question": "Welche Zuordnung ist KEINE Funktion?",
         "choices": ["x → 2x", "x → x²", "x → ±x", "x → x + 5"], "correct": 2},
        {"difficulty": 0.7, "step_complexity": 0.6, "qtype": "abstract",
         "question": "Eine Relation ordnet x = 2 die Werte y = 3 und y = 5 zu. Was gilt?",
         "choices": ["Es handelt sich um keine Funktion",
                     "Es handelt sich um eine Funktion",
                     "Es handelt sich um eine lineare Funktion",
                     "Der Definitionsbereich ist leer"],
         "correct": 0},
    ],
    "eq_reading": [
        {"difficulty": 0.2, "step_complexity": 0.2, "qtype": "abstract",
         "question": "Was beschreibt b in y = mx + b?",
         "choices": ["Die Steigung", "Den y-Achsenabschnitt", "Den Definitionsbereich", "Die Nullstelle"],
         "correct": 1},
        {"difficulty": 0.3, "step_complexity": 0.4, "qtype": "abstract",
         "question": "Was bedeutet m = -2 für den Graphen?",
         "choices": ["Die Funktion steigt", "Die Funktion fällt", "Die Funktion ist konstant", "Die Funktion ist quadratisch"],
         "correct": 1},
        {"difficulty": 0.5, "step_complexity": 0.7, "qtype": "abstract",
         "question": "Welche Funktion hat die größte Steigung?",
         "choices": ["y = 3x + 1", "y = -5x + 2", "y = x - 4", "y = 2x + 7"], "correct": 1},
        {"difficulty": 0.6, "step_complexity": 0.6, "qtype": "example",
         "question": "y = -3x + 6: Was lässt sich direkt ablesen?",
         "choices": ["Die Funktion fällt und schneidet die y-Achse bei 6",
                     "Die Funktion steigt und schneidet die y-Achse bei -3",
                     "Die Funktion ist konstant bei 6",
                     "Die Nullstelle liegt bei x = 6"],
         "correct": 0},
    ],
    "slope": [
        {"difficulty": 0.2, "step_complexity": 0.2, "qtype": "example",
         "question": "Wenn m = 4, was bedeutet das?",
         "choices": ["y steigt um 4 wenn x um 1 steigt", "y steigt um 1 wenn x um 4 steigt",
                     "y bleibt konstant", "x sinkt"],
         "correct": 0},
        {"difficulty": 0.5, "step_complexity": 0.5, "qtype": "abstract",
         "question": "Berechne die Steigung durch (1, 2) und (3, 6).",
         "choices": ["1", "2", "3", "4"], "correct": 1},
        {"difficulty": 0.4, "step_complexity": 0.7, "qtype": "abstract",
         "question": "Welche Gerade ist am steilsten?",
         "choices": ["m = 5", "m = -7", "m = 3", "m = -2"], "correct": 1},
        {"difficulty": 0.6, "step_complexity": 0.6, "qtype": "example",
         "question": "Ein Graph geht durch (0, 1) und (2, 5). Wie groß ist die Steigung?",
         "choices": ["1", "2", "3", "4"], "correct": 1},
    ],
    "graph_interp": [
        {"difficulty": 0.2, "step_complexity": 0.2, "qtype": "abstract",
         "question": "Wenn der Graph die y-Achse bei 3 schneidet, dann ist b = ?",
         "choices": ["0", "3", "-3", "1"], "correct": 1},
        {"difficulty": 0.3, "step_complexity": 0.4, "qtype": "abstract",
         "question": "Ein Graph fällt nach rechts. Was gilt?",
         "choices": ["m > 0", "m < 0", "m = 0", "b > 0"], "correct": 1},
        {"difficulty": 0.6, "step_complexity": 0.6, "qtype": "abstract",
         "question": "Wo liegt die Nullstelle von y = 2x - 4?",
         "choices": ["0", "1", "2", "4"], "correct": 2},
        {"difficulty": 0.8, "step_complexity": 0.6, "qtype": "abstract",
         "question": "Wann schneiden sich y = x + 1 und y = 2x - 1?",
         "choices": ["x = 1", "x = 2", "x = 3", "x = 0"], "correct": 1},
    ],
    "modelling": [
        {"difficulty": 0.3, "step_complexity": 0.4, "qtype": "example",
         "question": "3€ pro Stunde, 5€ Startgebühr. Welche Funktion beschreibt den Preis?",
         "choices": ["y = 3x + 5", "y = 5x + 3", "y = 3 + 5", "y = 5x - 3"], "correct": 0},
        {"difficulty": 0.4, "step_complexity": 0.6, "qtype": "example",
         "question": "Ein Tank hat 100 Liter. Pro Stunde fließen 8 Liter ab. Welche Funktion?",
         "choices": ["y = 100 - 8x", "y = 8x + 100", "y = 100 + 8x", "y = -100x + 8"], "correct": 0},
        {"difficulty": 0.6, "step_complexity": 0.6, "qtype": "example",
         "question": "Ein Handwerker berechnet 50€ Anfahrt + 40€ pro Stunde. Was kostet ein 3h-Einsatz?",
         "choices": ["150€", "170€", "190€", "210€"], "correct": 1},
        {"difficulty": 0.7, "step_complexity": 0.8, "qtype": "abstract",
         "question": "Bestimme die Gleichung der Geraden durch (0, 4) und (2, 8).",
         "choices": ["y = 2x + 4", "y = 4x + 2", "y = x + 4", "y = 2x - 4"], "correct": 0},
    ],
    "eq_manip": [
        {"difficulty": 0.3, "step_complexity": 0.2, "qtype": "abstract",
         "question": "Welche Operation isoliert x in 2x + 3 = 7?",
         "choices": ["Subtrahiere 3, dann dividiere durch 2",
                     "Addiere 3, dann multipliziere mit 2",
                     "Dividiere durch 2, dann subtrahiere 3",
                     "Multipliziere mit 2, dann subtrahiere 3"],
         "correct": 0},
        {"difficulty": 0.5, "step_complexity": 0.4, "qtype": "example",
         "question": "Löse 3x - 5 = 10.",
         "choices": ["x = 5", "x = 3", "x = 15", "x = -5"], "correct": 0},
        {"difficulty": 0.7, "step_complexity": 0.6, "qtype": "abstract",
         "question": "Löse 2(x + 3) - 4 = 10.",
         "choices": ["x = 4", "x = 3", "x = 5", "x = 6"], "correct": 0},
        {"difficulty": 0.8, "step_complexity": 0.7, "qtype": "abstract",
         "question": "Löse 3(x - 2) = 2x + 1.",
         "choices": ["x = 5", "x = 7", "x = 3", "x = 1"], "correct": 1},
    ],
    "application": [
        {"difficulty": 0.2, "step_complexity": 0.2, "qtype": "example",
         "question": "Wenn m negativ ist, bedeutet das für eine reale Größe?",
         "choices": ["Die Größe nimmt ab", "Die Größe nimmt zu", "Die Größe bleibt konstant", "Keine Aussage möglich"],
         "correct": 0},
        {"difficulty": 0.3, "step_complexity": 0.4, "qtype": "example",
         "question": "Was bedeutet b = 100 in y = 20x + 100 als Kostenmodell?",
         "choices": ["Fixkosten von 100€", "Variable Kosten pro Einheit", "Gesamtgewinn", "Anzahl der Einheiten"],
         "correct": 0},
        {"difficulty": 0.6, "step_complexity": 0.7, "qtype": "abstract",
         "question": "y = 3x + 1 und y = 3x - 4: Was gilt für diese Geraden?",
         "choices": ["Sie sind parallel", "Sie schneiden sich genau einmal", "Sie sind identisch", "Sie stehen senkrecht aufeinander"],
         "correct": 0},
        {"difficulty": 0.8, "step_complexity": 0.6, "qtype": "example",
         "question": "Anbieter A: y = 10x + 50, Anbieter B: y = 15x + 20. Ab welchem x ist A günstiger?",
         "choices": ["ab x = 4", "ab x = 6", "ab x = 8", "ab x = 10"], "correct": 1},
    ],
}

SUBJECT_LABELS = {
    "func_concept": "Funktionsbegriff",
    "eq_reading":   "Gleichungen lesen",
    "slope":        "Steigung",
    "graph_interp": "Graphen deuten",
    "modelling":    "Modellierung",
    "eq_manip":     "Gleichungen umformen",
    "application":  "Anwendungen",
}

# ─────────────────────────────────────────────────────────────────
# SESSION HELPERS  – replace the in-memory `user` object
# ─────────────────────────────────────────────────────────────────

def default_profile(name="Lernender"):
    return {
        "name": name,
        "psychometrics": {
            "complexity": 0.0,
            "abstract_pref": 0.5,
            "meta_accuracy": {"false_pos": 0.2, "false_neg": 0.2},
        },
        "subject_skills": {k: 0.0 for k in assessment_questions},
        "solved": [],
        "_cat_solved": {k: [] for k in assessment_questions},
        "performances": [],
        "testscores": [],
        "assessment_done": False,
        "xp": 0,
        "streak": 0,
        "last_correct": False,
    }

def get_profile():
    if "profile" not in session:
        session["profile"] = default_profile()
    return session["profile"]

def save_profile(p):
    session["profile"] = p
    session.modified = True

# ─────────────────────────────────────────────────────────────────
# PSYCHOMETRIC LOGIC  (identical algorithms, session-based)
# ─────────────────────────────────────────────────────────────────

def update_skill(profile, subject, ex_id, support, errors):
    """Unchanged algorithm from MVP."""
    difficulty = Exercises[subject][ex_id]["difficulty"]
    skill = profile["subject_skills"][subject]
    performance = max(0, 1 - 0.2 * errors)
    if support is None:
        if difficulty > skill:
            skill += 0.15 * difficulty * performance
    else:
        if difficulty < skill:
            skill -= 0.15 * difficulty * (1 - performance)
    profile["subject_skills"][subject] = round(max(0.0, min(1.0, skill)), 10)
    solved = profile["solved"]
    if [subject, ex_id] not in solved:
        solved.append([subject, ex_id])
    profile["solved"] = solved


def update_psychometrics(profile, support, errors):
    """Unchanged algorithm from MVP."""
    ma = profile["psychometrics"]["meta_accuracy"]
    if errors == 0:
        if support == "strategy":
            ma["false_pos"] = max(0, ma["false_pos"] - 0.1)
        if support == "scaffold":
            profile["psychometrics"]["complexity"] = min(1, profile["psychometrics"]["complexity"] + 0.1)
    elif errors > 1:
        if support == "strategy":
            ma["false_pos"] = min(1, ma["false_pos"] + 0.1)
        if support == "scaffold":
            profile["psychometrics"]["complexity"] = max(0, profile["psychometrics"]["complexity"] - 0.1)
    profile["psychometrics"]["meta_accuracy"] = ma


def calculate_attention(profile, errors):
    """Unchanged algorithm. Returns True if break is suggested."""
    profile["performances"].append(max(0, 1 - 0.2 * errors))
    perfs = profile["performances"]
    if len(perfs) >= 5:
        five_avg  = sum(perfs[-5:]) / 5
        three_avg = sum(perfs[-3:]) / 3
        if three_avg - five_avg < -0.2:
            return True
    return False


def choose_subject(profile):
    """Unchanged algorithm from MVP."""
    skills = profile["subject_skills"]
    weak   = [k for k, v in skills.items() if v < 0.4]
    mid    = [k for k, v in skills.items() if 0.4 <= v < 0.7]
    strong = [k for k, v in skills.items() if v >= 0.7]
    roll   = r.randint(1, 10)
    if roll <= 5 and weak:   return r.choice(weak)
    if roll <= 8 and mid:    return r.choice(mid)
    if strong:               return r.choice(strong)
    return r.choice(list(skills.keys()))


def choose_exercise(profile):
    """Unchanged algorithm from MVP."""
    subject   = choose_subject(profile)
    exercises = Exercises.get(subject, [])
    if not exercises:
        return subject, 0

    solved = [tuple(s) for s in profile["solved"]]
    diffs  = [abs(ex["difficulty"] - profile["subject_skills"][subject]) for ex in exercises]
    choice = diffs.index(min(diffs))

    if (subject, choice) not in solved:
        return subject, choice

    sorted_ids = sorted(range(len(diffs)), key=lambda i: diffs[i])
    for candidate in sorted_ids:
        if (subject, candidate) not in solved:
            return subject, candidate

    remaining = [k for k in profile["subject_skills"] if
                 any((k, i) not in solved for i in range(len(Exercises.get(k, []))))]
    if not remaining:
        return subject, choice
    profile["subject_skills"][subject] = -1
    result = choose_exercise(profile)
    profile["subject_skills"][subject] += 1
    return result


def get_representation(profile, subject, ex_id):
    """Unchanged algorithm from MVP."""
    ex   = Exercises[subject][ex_id]
    pref = profile["psychometrics"]["abstract_pref"]
    roll = r.random()
    if roll > 0.8:
        return ex["representations"]["mixed"]
    elif roll < pref:
        return ex["representations"]["abstract"]
    else:
        return ex["representations"]["example"]


def get_support_type(profile, subject, ex_id):
    """Determine whether strategy, scaffold or None support applies."""
    ex = Exercises[subject][ex_id]
    fp = profile["psychometrics"]["meta_accuracy"]["false_pos"]
    complexity_diff = profile["psychometrics"]["complexity"] - ex["step_complexity"]
    if fp > 0.4:
        return "strategy"
    elif complexity_diff < 0:
        return "scaffold"
    return None


def get_strategy_questions(profile, subject, ex_id):
    ex    = Exercises[subject][ex_id]
    fp    = profile["psychometrics"]["meta_accuracy"]["false_pos"]
    level = "full" if fp > 0.6 else "light"
    return ex.get("strategy", {}).get(level, [])


def get_scaffold_steps(profile, subject, ex_id):
    ex   = Exercises[subject][ex_id]
    diff = ex["step_complexity"] - profile["psychometrics"]["complexity"]
    if diff > 0.3:
        level = "full"
    elif diff > 0.0:
        level = "light"
    else:
        return []
    return ex.get("scaffolding", {}).get(level, [])


# ─────────────────────────────────────────────────────────────────
# ASSESSMENT HELPERS (unchanged logic)
# ─────────────────────────────────────────────────────────────────

def assessment_ban(profile, category, i, is_correct, confidence):
    questions            = assessment_questions[category]
    current_difficulty   = questions[i]["difficulty"]
    current_step_complex = questions[i]["step_complexity"]
    banned = set(tuple(b) for b in profile.get("assessment_banned", []))

    if is_correct and confidence > 0.7:
        for j, q in enumerate(questions):
            if q["difficulty"] < current_difficulty:
                banned.add((category, j))
    elif not is_correct and confidence >= 0.7:
        for j, q in enumerate(questions):
            if q["step_complexity"] > current_step_complex:
                banned.add((category, j))
    elif not is_correct and confidence < 0.7:
        for j, q in enumerate(questions):
            if q["difficulty"] > current_difficulty:
                banned.add((category, j))

    profile["assessment_banned"] = [list(b) for b in banned]


def assessment_update_profile(profile, is_correct, confidence, category, i):
    """Unchanged algorithm from MVP."""
    q  = assessment_questions[category][i]
    ma = profile["psychometrics"]["meta_accuracy"]
    cs = profile.get("_confidently_solved", [])
    us = profile.get("_unconf_solved", [])

    if is_correct:
        if confidence <= 0.7:
            ma["false_neg"] = min(ma["false_neg"] + 0.1, 1.0)
        else:
            ma["false_neg"] = max(ma["false_neg"] - 0.05, 0.0)
    else:
        if confidence >= 0.7:
            ma["false_pos"] = min(ma["false_pos"] + 0.1, 1.0)
        else:
            ma["false_pos"] = max(ma["false_pos"] - 0.05, 0.0)

    if is_correct:
        if confidence > 0.7:
            cs.append(q["step_complexity"])
        else:
            us.append(q["step_complexity"])

        cat_solved = profile["_cat_solved"][category]
        cat_solved.append({"difficulty": q["difficulty"], "confidence": confidence})
        cat_results = sorted(cat_solved, key=lambda x: x["difficulty"])
        hardest = cat_results[-1]

        if hardest["confidence"] > 0.7:
            profile["subject_skills"][category] = min(hardest["difficulty"], 1.0)
        elif len(cat_results) >= 2:
            second = cat_results[-2]["difficulty"]
            profile["subject_skills"][category] = min(
                (hardest["difficulty"] + second) / 2, 1.0)
        else:
            profile["subject_skills"][category] = min(hardest["difficulty"] * 0.75, 1.0)

    if cs and us:
        mean_conf  = sum(cs) / len(cs)
        min_unconf = min(us)
        profile["psychometrics"]["complexity"] = (mean_conf + min_unconf) / 2
    elif cs:
        profile["psychometrics"]["complexity"] = sum(cs) / len(cs)
    elif us:
        profile["psychometrics"]["complexity"] = min(us) * 0.75

    profile["psychometrics"]["meta_accuracy"] = ma
    profile["_confidently_solved"] = cs
    profile["_unconf_solved"]       = us


def assessment_update_abstract_pref(profile, qtype, is_correct):
    """Unchanged algorithm from MVP."""
    if is_correct:
        if qtype == "abstract":
            profile["psychometrics"]["abstract_pref"] = min(
                profile["psychometrics"]["abstract_pref"] + 0.05, 1.0)
        else:
            profile["psychometrics"]["abstract_pref"] = max(
                profile["psychometrics"]["abstract_pref"] - 0.05, 0.0)


# ─────────────────────────────────────────────────────────────────
# XP / GAMIFICATION
# ─────────────────────────────────────────────────────────────────

XP_CORRECT        = 20
XP_CORRECT_STREAK = 10   # bonus per streak step
XP_WRONG          = -5


def award_xp(profile, correct, errors=0):
    if correct and errors == 0:
        profile["streak"] = profile.get("streak", 0) + 1
        bonus = min(profile["streak"] - 1, 5) * XP_CORRECT_STREAK
        profile["xp"] = profile.get("xp", 0) + XP_CORRECT + bonus
    else:
        profile["streak"] = 0
        profile["xp"] = max(0, profile.get("xp", 0) + XP_WRONG)


def xp_level(xp):
    """Returns (level, xp_in_level, xp_needed_for_next)."""
    thresholds = [0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200, 4000]
    for i, t in enumerate(thresholds):
        if xp < t:
            prev = thresholds[i - 1]
            return i, xp - prev, t - prev
    return len(thresholds), xp - thresholds[-1], 500


# ─────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    profile = get_profile()
    level, xp_in, xp_need = xp_level(profile.get("xp", 0))
    skills = {SUBJECT_LABELS[k]: round(v * 100) for k, v in profile["subject_skills"].items()}
    return render_template("index.html",
                           profile=profile,
                           level=level,
                           xp_in=xp_in,
                           xp_need=xp_need,
                           skills=skills,
                           subject_labels=SUBJECT_LABELS)


@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))


# ── ASSESSMENT ────────────────────────────────────────────────────

@app.route("/assessment", methods=["GET"])
def assessment_start():
    profile = get_profile()
    if profile.get("assessment_done"):
        return redirect(url_for("index"))
    # Build ordered list of (category, question_index) to ask
    order = [1, 2, 3, 0]
    queue = []
    for cat in assessment_questions:
        for i in order:
            queue.append({"category": cat, "index": i})
    profile["assessment_queue"]   = queue
    profile["assessment_ptr"]     = 0
    profile["assessment_banned"]  = []
    profile["_confidently_solved"] = []
    profile["_unconf_solved"]      = []
    save_profile(profile)
    return redirect(url_for("assessment_question"))


@app.route("/assessment/question", methods=["GET"])
def assessment_question():
    profile = get_profile()
    queue   = profile.get("assessment_queue", [])
    ptr     = profile.get("assessment_ptr", 0)
    banned  = [list(b) for b in profile.get("assessment_banned", [])]

    # Advance past banned questions
    while ptr < len(queue):
        item = queue[ptr]
        if [item["category"], item["index"]] in banned:
            ptr += 1
        else:
            break

    if ptr >= len(queue):
        profile["assessment_done"] = True
        save_profile(profile)
        return redirect(url_for("assessment_done"))

    profile["assessment_ptr"] = ptr
    save_profile(profile)

    item = queue[ptr]
    cat  = item["category"]
    idx  = item["index"]
    q    = assessment_questions[cat][idx]

    total_asked = ptr
    total       = len(queue)

    return render_template("assessment_question.html",
                           question=q,
                           category=cat,
                           cat_label=SUBJECT_LABELS.get(cat, cat),
                           q_index=idx,
                           progress=round(ptr / total * 100) if total else 0,
                           q_num=ptr + 1,
                           total=total)


@app.route("/assessment/answer", methods=["POST"])
def assessment_answer():
    profile    = get_profile()
    category   = request.form["category"]
    q_index    = int(request.form["q_index"])
    user_ans   = int(request.form["answer"])
    confidence = float(request.form["confidence"])

    q          = assessment_questions[category][q_index]
    is_correct = (user_ans == q["correct"])

    assessment_ban(profile, category, q_index, is_correct, confidence)
    assessment_update_profile(profile, is_correct, confidence, category, q_index)
    assessment_update_abstract_pref(profile, q["qtype"], is_correct)

    profile["assessment_ptr"] = profile.get("assessment_ptr", 0) + 1
    save_profile(profile)

    return jsonify({
        "correct":       is_correct,
        "correct_index": q["correct"],
        "explanation":   q.get("explanation", "")
    })


@app.route("/assessment/done")
def assessment_done():
    profile = get_profile()
    skills  = {SUBJECT_LABELS[k]: round(v * 100) for k, v in profile["subject_skills"].items()}
    level, xp_in, xp_need = xp_level(profile.get("xp", 0))
    return render_template("assessment_done.html",
                           profile=profile,
                           skills=skills,
                           level=level,
                           xp_in=xp_in,
                           xp_need=xp_need)


# ── EXERCISE (main learning loop) ────────────────────────────────

@app.route("/exercise", methods=["GET"])
def exercise():
    profile = get_profile()
    if not profile.get("assessment_done"):
        return redirect(url_for("assessment_start"))
    if not Exercises:
        return render_template("no_data.html", msg="exercises.json fehlt.")

    subject, ex_id  = choose_exercise(profile)
    support_type    = get_support_type(profile, subject, ex_id)
    rep_text        = get_representation(profile, subject, ex_id)
    ex              = Exercises[subject][ex_id]

    # Persist current exercise state
    profile["current_exercise"] = {
        "subject":      subject,
        "ex_id":        ex_id,
        "support_type": support_type,
        "errors":       0,
        "support_step": 0,   # which scaffold/strategy step we're on
        "phase":        "support" if support_type else "main",
    }
    save_profile(profile)

    level, xp_in, xp_need = xp_level(profile.get("xp", 0))
    skills = {k: round(v * 100) for k, v in profile["subject_skills"].items()}

    return render_template("exercise.html",
                           ex=ex,
                           subject=subject,
                           subject_label=SUBJECT_LABELS.get(subject, subject),
                           ex_id=ex_id,
                           support_type=support_type,
                           rep_text=rep_text,
                           profile=profile,
                           level=level,
                           xp_in=xp_in,
                           xp_need=xp_need,
                           skills=skills,
                           subject_labels=SUBJECT_LABELS)


@app.route("/exercise/support_step", methods=["POST"])
def exercise_support_step():
    """Handle one scaffold / strategy sub-question answer."""
    profile = get_profile()
    ce      = profile.get("current_exercise", {})
    subject = ce["subject"]
    ex_id   = ce["ex_id"]
    step_i  = ce["support_step"]
    support = ce["support_type"]

    if support == "strategy":
        steps = get_strategy_questions(profile, subject, ex_id)
    else:
        steps = get_scaffold_steps(profile, subject, ex_id)

    if step_i >= len(steps):
        return jsonify({"done": True})

    step       = steps[step_i]
    user_ans   = request.form.get("answer", "").strip()

    if support == "strategy":
        is_correct = user_ans.isdigit() and int(user_ans) == step["correct"]
        hint       = step.get("explanation", "")
    else:
        is_correct = user_ans == str(step.get("answer", ""))
        hint       = step.get("hint", "")

    if not is_correct:
        ce["errors"] += 1

    ce["support_step"] = step_i + 1
    profile["current_exercise"] = ce
    save_profile(profile)

    next_step = steps[step_i + 1] if step_i + 1 < len(steps) else None
    return jsonify({
        "correct":   is_correct,
        "hint":      hint,
        "done":      (step_i + 1 >= len(steps)),
        "next_step": next_step
    })


@app.route("/exercise/answer", methods=["POST"])
def exercise_answer():
    """Handle the main exercise answer."""
    profile = get_profile()
    ce      = profile.get("current_exercise", {})
    subject = ce["subject"]
    ex_id   = ce["ex_id"]
    ex      = Exercises[subject][ex_id]

    user_ans = request.form.get("answer", "").strip()

    if ex["ans_type"] == "input":
        is_correct = (user_ans == str(ex["final_answer"]))
    else:
        # final_answer is 0-based string index; user_ans comes in as "0","1",...
        is_correct = (user_ans == str(ex["final_answer"]))

    if is_correct:
        ce["errors"] = ce.get("errors", 0)  # don't add
    else:
        ce["errors"] = ce.get("errors", 0) + 1
        profile["current_exercise"] = ce
        save_profile(profile)
        hint = ex.get("error_feedback", {}).get("concept_hint", "")
        return jsonify({"correct": False, "hint": hint})

    # ── correct answer path ──────────────────────────────────────
    errors       = ce.get("errors", 0)
    support_type = ce.get("support_type")

    update_skill(profile, subject, ex_id, support_type, errors)
    update_psychometrics(profile, support_type, errors)
    need_break = calculate_attention(profile, errors)
    award_xp(profile, True, errors)

    level, xp_in, xp_need = xp_level(profile.get("xp", 0))
    save_profile(profile)

    return jsonify({
        "correct":    True,
        "xp":         profile["xp"],
        "level":      level,
        "streak":     profile["streak"],
        "need_break": need_break,
        "skills":     {k: round(v * 100) for k, v in profile["subject_skills"].items()},
    })


# ── HELP / EXPLANATIONS ──────────────────────────────────────────

@app.route("/help")
def help_page():
    profile = get_profile()
    level, xp_in, xp_need = xp_level(profile.get("xp", 0))
    return render_template("help.html", subjects=SUBJECT_LABELS, profile=profile, level=level, xp_in=xp_in, xp_need=xp_need)


@app.route("/help/<subject>")
def help_subject(subject):
    if subject not in SUBJECT_LABELS:
        return redirect(url_for("help_page"))
    if not Explanations:
        return render_template("no_data.html", msg="explanations.json fehlt.")

    profile = get_profile()
    comp    = "low_complexity" if profile["psychometrics"]["complexity"] <= 0.4 else "high_complexity"
    pref    = "abstract" if profile["psychometrics"]["abstract_pref"] > 0.5 else "example"

    expl = Explanations.get(subject, {}).get(pref, {}).get(comp, {})
    steps = expl.get("steps", [])

    level, xp_in, xp_need = xp_level(profile.get("xp", 0))

    # Resolve visualization URLs for each step
    steps_with_viz = []
    for step in steps:
        s = dict(step)
        s["viz_url"] = viz_url(step.get("visualization"))
        steps_with_viz.append(s)

    return render_template("help_subject.html",
                           subject=subject,
                           subject_label=SUBJECT_LABELS[subject],
                           steps=steps_with_viz,
                           profile=profile,
                           pref=pref,
                           comp=comp,
                           level=level,
                           xp_in=xp_in,
                           xp_need=xp_need)


@app.route("/help/<subject>/check", methods=["POST"])
def help_check(subject):
    step_i   = int(request.form["step_index"])
    user_ans = request.form.get("answer", "").strip()
    profile  = get_profile()

    comp = "low_complexity" if profile["psychometrics"]["complexity"] <= 0.4 else "high_complexity"
    pref = "abstract" if profile["psychometrics"]["abstract_pref"] > 0.5 else "example"

    steps = Explanations.get(subject, {}).get(pref, {}).get(comp, {}).get("steps", [])
    if step_i >= len(steps):
        return jsonify({"correct": False, "hint": ""})

    step       = steps[step_i]
    correct_a  = str(step["practice"]["answer"]).strip()
    is_correct = (user_ans == correct_a)
    hint       = step["practice"].get("hint", "")

    return jsonify({"correct": is_correct, "hint": hint})


# ── TEST ─────────────────────────────────────────────────────────

@app.route("/test")
def test_page():
    profile = get_profile()
    if not Tests:
        return render_template("no_data.html", msg="testing.json fehlt.")
    i    = len(profile.get("testscores", [])) % len(Tests)
    test = Tests[i]
    level, xp_in, xp_need = xp_level(profile.get("xp", 0))
    return render_template("test.html",
                           test=test,
                           test_index=i,
                           profile=profile,
                           level=level,
                           xp_in=xp_in,
                           xp_need=xp_need)


@app.route("/test/submit", methods=["POST"])
def test_submit():
    profile = get_profile()
    if not Tests:
        return jsonify({"error": "No tests"})

    i    = len(profile.get("testscores", [])) % len(Tests)
    test = Tests[i]

    score   = 0
    results = []
    for j, elem in enumerate(test):
        user_ans    = request.form.get(f"q{j}", "").strip()
        correct_ans = str(elem["answer"]).strip()
        is_correct  = (user_ans == correct_ans)
        if is_correct:
            score += 1
        results.append({
            "question":    elem["question"]["question"],
            "user_ans":    user_ans,
            "correct_ans": correct_ans,
            "correct":     is_correct,
        })

    profile["testscores"].append(score)
    xp_bonus = score * 15
    profile["xp"] = profile.get("xp", 0) + xp_bonus
    save_profile(profile)

    level, xp_in, xp_need = xp_level(profile.get("xp", 0))
    return jsonify({
        "score":   score,
        "total":   len(test),
        "xp":      profile["xp"],
        "xp_bonus": xp_bonus,
        "level":   level,
        "results": results,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
