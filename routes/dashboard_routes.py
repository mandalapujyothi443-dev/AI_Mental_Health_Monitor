from flask import Blueprint, render_template
from utils.database import get_db
from utils.security import role_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/counselor/dashboard")
@role_required("counselor")
def counselor_dashboard():
    db = get_db()

    stats = db.execute("""
        SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN risk_level='Low Concern' THEN 1 ELSE 0 END) AS low,
        SUM(CASE WHEN risk_level='Needs Attention' THEN 1 ELSE 0 END) AS attention,
        SUM(CASE WHEN risk_level='Human Review' THEN 1 ELSE 0 END) AS review
        FROM assessments
    """).fetchone()

    recent = db.execute("""
        SELECT a.*, u.name
        FROM assessments a
        JOIN users u ON u.id=a.user_id
        ORDER BY a.created_at DESC
        LIMIT 20
    """).fetchall()

    db.close()
    return render_template(
        "counselor_dashboard.html",
        stats=stats,
        assessments=recent
    )
