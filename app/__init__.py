from flask import Flask
from flask_cors import CORS
from flask_injector import FlaskInjector
from di.di_container import configure
from app.routes.llmRouter import api

def create_app():
    app = Flask(__name__)
    cors = CORS(app)
    app.register_blueprint(api, url_prefix="/api")
    app.config['CORS_HEADER'] = 'Content-Type'
    FlaskInjector(app=app, modules=[configure])

    return app