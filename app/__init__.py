import os
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

    from .models import init_db
    init_db()

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .auth import auth_bp
    from .routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
