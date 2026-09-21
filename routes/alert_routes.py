from flask import Blueprint, render_template, redirect, url_for, flash
from utils.database import get_db
from utils.security import role_required

alert_bp = Blueprint("alert", __name__)

@alert_bp.route("/alerts")
@role_required("counselor")
def alerts():
    db = get_db()
    rows = db.execute("""
        SELECT alerts.*, users.name
        FROM alerts
        JOIN users ON users.id=alerts.user_id
        ORDER BY alerts.created_at DESC
    """).fetchall()
    db.close()
    return render_template("alerts.html", alerts=rows)

@alert_bp.route("/alerts/<int:alert_id>/resolve", methods=["POST"])
@role_required("counselor")
def resolve(alert_id):
    db = get_db()
    db.execute("UPDATE alerts SET status='Reviewed' WHERE id=?", (alert_id,))
    db.commit()
    db.close()
    flash("Alert marked as reviewed.", "success")
    return redirect(url_for("alert.alerts"))
