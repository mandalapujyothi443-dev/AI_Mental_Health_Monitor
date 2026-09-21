from flask import Blueprint, render_template, session
from utils.database import get_db
from utils.security import login_required

user_bp = Blueprint("user", __name__)

@user_bp.route("/")
def index():
    return render_template("index.html")

@user_bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    assessments = db.execute(
        """SELECT * FROM assessments WHERE user_id=?
           ORDER BY created_at DESC LIMIT 5""",
        (session["user_id"],)
    ).fetchall()
    db.close()
    return render_template("user_dashboard.html", assessments=assessments)
