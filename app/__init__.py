from flask import Flask
from flask_cors import CORS

import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    from .routes import riot_bp
    app.register_blueprint(riot_bp)

    return app
