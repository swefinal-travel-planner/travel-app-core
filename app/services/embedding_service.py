from injector import inject
from sentence_transformers import SentenceTransformer

def get_embedding_model(model_name):

    local_model_path = "./model_ai/vietnamese_embedding"

    try:
        print("Loading model from local path...")
        return SentenceTransformer(local_model_path)
    except:
        print("Model not found locally, downloading...")
        model = SentenceTransformer(model_name)
        model.save(local_model_path)
        print("Model downloaded and saved locally.")
        return model

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