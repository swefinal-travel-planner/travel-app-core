from injector import inject
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    
    @inject
    def __init__(self, model=None):
        self.model = SentenceTransformer(model)

        if not self.model:
            print("Could not load the model.")
        else:
            print("Model loaded successfully.")

    def embed_text(self, text):
        return self.model.encode(text)