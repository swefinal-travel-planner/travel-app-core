import os
import py_vncorenlp
from injector import inject
from sentence_transformers import CrossEncoder

def get_vncorenlp_model(save_dir):
    py_vncorenlp.download_model(save_dir=save_dir)
    return py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir=save_dir)

def get_cross_encoder_model(model_name, local_path, max_length = 256):
    try:
        return CrossEncoder(local_path, max_length=max_length)
    except:
        print("Model not found locally, downloading...")
        model = CrossEncoder(model_name, max_length=max_length)
        model.save(local_path)
        print("Model downloaded and saved locally.")
        return model.model

class RerankerService:
    @inject
    def __init__(self, model_name):

        vncorenlp_path = "./model_ai/py_vncorenlp"
        rerank_path = "./model_ai/pho_ranker"

        #self.__rdrsegmenter = get_vncorenlp_model(vncorenlp_path)
        #self.__rerank_model = get_cross_encoder_model(model_name, rerank_path, 256)
        
        print("Reranker model loaded successfully.")

    def word_segment(self, text: str):
        return self.__rdrsegmenter.word_segment(text)
    
    def rerank(self, query: str, candidates: list):
        if not candidates:
            return []
        
        # Preprocess the query and candidates
        query = self.word_segment(query)
        candidates = [self.word_segment(candidate) for candidate in candidates]

        # Rerank the candidates
        reranked_candidates = self.__rerank_model.predict([(query, candidate) for candidate in candidates], convert_to_tensor=True)

        # Sort candidates based on their scores
        sorted_candidates = sorted(zip(candidates, reranked_candidates), key=lambda x: x[1], reverse=True)

        return [candidate for candidate, score in sorted_candidates]