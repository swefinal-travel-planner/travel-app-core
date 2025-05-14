import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME")
    ELASTIC_HOST = os.getenv('ES_HOST')
    ELASTIC_PORT = os.getenv('ES_PORT')
    ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
    ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
    EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME')
    MAPBOX_API_KEY = os.getenv('MAPBOX_API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')