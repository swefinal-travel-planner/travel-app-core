from app.repositories.place_repository import PlaceRepository
from app.services.embedding_service import EmbeddingService
from injector import inject

class PlaceService:
    @inject
    def __init__(self, place_repository: PlaceRepository,embedding_service: EmbeddingService):
        self.place_repository = place_repository
        self.embedding_service = embedding_service

    def embed_text(self, text):
        return self.embedding_service.embed_text(text)