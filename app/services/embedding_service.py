from injector import inject
from sentence_transformers import SentenceTransformer

from functools import lru_cache

@lru_cache(maxsize=1)
def get_embedding_model(model_name):
    return SentenceTransformer(model_name)

class EmbeddingService:
    
    @inject
    def __init__(self, model=None):
        self.__model = get_embedding_model(model) if model else None

        if not self.__model:
            print("Could not load the model.")
        else:
            print("Model embedding loaded successfully.")

    def embed_text(self, text):
        return self.__model.encode(text)