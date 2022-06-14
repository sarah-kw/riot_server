from flask import Flask

import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    from .routes import riot_bp
    app.register_blueprint(riot_bp)

    return app
