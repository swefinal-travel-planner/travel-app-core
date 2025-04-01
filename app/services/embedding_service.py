from injector import inject
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    
    @inject
    def __init__(self, model=None):
        self.__model = SentenceTransformer(model)

        if not self.__model:
            print("Could not load the model.")
        else:
            print("Model embedding loaded successfully.")

    def embed_text(self, text):
        return self.__model.encode(text)