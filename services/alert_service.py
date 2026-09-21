from utils.database import get_db

def create_alert_if_needed(user_id, assessment_id, risk_level):
    if risk_level not in ("Needs Attention", "Human Review"):
        return

    message = (
        "A recent wellbeing assessment produced a concerning pattern. "
        "Please review the information and follow your organization's "
        "appropriate human-support and safeguarding process."
    )

    db = get_db()
    db.execute(
        """INSERT INTO alerts(user_id, assessment_id, risk_level, message)
           VALUES(?,?,?,?)""",
        (user_id, assessment_id, risk_level, message)
    )
    db.commit()
    db.close()
