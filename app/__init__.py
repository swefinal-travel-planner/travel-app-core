from flask import Flask
from flask_cors import CORS
from flask_injector import FlaskInjector
from di.di_container import configure
from app.routes.router import api
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    
    # Configure Swagger
    app.config['SWAGGER'] = {
        'title': 'Travel App API',
        'uiversion': 3
    }
    swagger = Swagger(app)
    
    cors = CORS(app)
    app.register_blueprint(api, url_prefix="/api")
    app.config['CORS_HEADER'] = 'Content-Type'
    FlaskInjector(app=app, modules=[configure])
    
    return app