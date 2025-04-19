from injector import Module, singleton, provider
from app.controllers.place_controller import PlaceController
from app.controllers.tour_controller import TourController
from app.database.elasticsearch import ElasticsearchClient
from app.repositories.place_repository import PlaceRepository
from app.services.place_service import PlaceService
from app.services.tour_service import TourService
from app.services.embedding_service import EmbeddingService
from app.services.distance_matrix_service import DistanceMatrixService
from app.services.openai_service import OpenAIService
from config.config import Config

class MainModule(Module):
    # Database
    @singleton
    @provider
    def provide_elasticsearch_client(self) -> ElasticsearchClient:
        return ElasticsearchClient(Config.ELASTIC_HOST, int(Config.ELASTIC_PORT), Config.ELASTIC_USERNAME, Config.ELASTIC_PASSWORD)
    
    # Bind the services and controllers to their respective modules
    #Repository
    @singleton
    @provider
    def provide_place_repository(self, db: ElasticsearchClient) -> PlaceRepository:
        return PlaceRepository(db)
    
    #Service
    @singleton
    @provider
    def provide_place_service(self, 
                            place_repository: PlaceRepository,
                            embedding_service: EmbeddingService,
                            distance_matrix_service: DistanceMatrixService,
                            openai_service: OpenAIService) -> PlaceService:
        return PlaceService(place_repository, 
                            embedding_service, 
                            distance_matrix_service,
                            openai_service)
    
    @singleton
    @provider
    def provide_tour_service(self, openai_service: OpenAIService) -> TourService:
        return TourService(openai_service)
    
    @singleton
    @provider
    def provide_embedding_service(self) -> EmbeddingService:
        return EmbeddingService(Config.EMBEDDING_MODEL_NAME)
    
    @singleton
    @provider
    def provide_distance_matrix_service(self) -> DistanceMatrixService:
        return DistanceMatrixService(Config.MAPBOX_API_KEY)
    
    @singleton
    @provider
    def provide_openai_service(self) -> OpenAIService:
        return OpenAIService(Config.OPENAI_API_KEY, Config.MODEL_NAME)
    
    #Controller
    @singleton
    @provider
    def provide_place_controller(self, place_service: PlaceService) -> PlaceController:
        return PlaceController(place_service)
    
    @singleton
    @provider
    def provide_tour_controller(self, tour_service: TourService) -> TourController:
        return TourController(tour_service)


def configure(binder):
    binder.install(MainModule())
