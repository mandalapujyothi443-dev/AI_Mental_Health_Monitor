from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.database import get_db
from utils.security import login_required
from utils.validators import score
from services.sentiment_service import text_indicator_score
from services.distress_service import calculate_distress
from services.ai_service import analyze_text
from services.alert_service import create_alert_if_needed

assessment_bp = Blueprint("assessment", __name__)

@assessment_bp.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    if request.method == "POST":
        try:
            mood = score(request.form.get("mood_score"), "Mood")
            stress = score(request.form.get("stress_score"), "Stress")
            sleep = score(request.form.get("sleep_score"), "Sleep")
            activity = score(request.form.get("activity_score"), "Activity")
            text_input = request.form.get("text_input", "").strip()

            text_score = text_indicator_score(text_input)
            distress_score, risk_level = calculate_distress(
                mood, stress, sleep, activity, text_score
            )
            ai_summary = analyze_text(text_input)

            db = get_db()
            cursor = db.execute(
                """INSERT INTO assessments
                (user_id,mood_score,stress_score,sleep_score,activity_score,
                 text_input,distress_score,risk_level,ai_summary)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    session["user_id"], mood, stress, sleep, activity,
                    text_input, distress_score, risk_level, ai_summary
                )
            )
            assessment_id = cursor.lastrowid
            db.commit()
            db.close()

            create_alert_if_needed(
                session["user_id"], assessment_id, risk_level
            )

            return redirect(url_for(
                "assessment.result", assessment_id=assessment_id
            ))

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("assessment.html")

@assessment_bp.route("/assessment/result/<int:assessment_id>")
@login_required
def result(assessment_id):
    db = get_db()
    row = db.execute(
        """SELECT * FROM assessments
           WHERE id=? AND user_id=?""",
        (assessment_id, session["user_id"])
    ).fetchone()
    db.close()

    if not row:
        flash("Assessment not found.", "danger")
        return redirect(url_for("user.dashboard"))

    return render_template("result.html", assessment=row)

@assessment_bp.route("/history")
@login_required
def history():
    db = get_db()
    rows = db.execute(
        """SELECT * FROM assessments WHERE user_id=?
           ORDER BY created_at DESC""",
        (session["user_id"],)
    ).fetchall()
    db.close()
    return render_template("history.html", assessments=rows)
