from flask import Flask, redirect, url_for
from config import Config
from utils.database import init_db
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.assessment_routes import assessment_bp
from routes.dashboard_routes import dashboard_bp
from routes.alert_routes import alert_bp
from routes.assistant_routes import assistant_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # FIX: initialize database inside Flask application context
    with app.app_context():
        init_db()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(assistant_bp)

    @app.route("/")
    def index():
        return redirect(url_for("user.index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)