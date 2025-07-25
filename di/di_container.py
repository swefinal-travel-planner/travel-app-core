from injector import Module, singleton, provider
from app.controllers.distance_time_controller import DistanceTimeController
from app.controllers.place_controller import PlaceController
from app.controllers.tour_controller import TourController
from app.database.elasticsearch import ElasticsearchClient
from app.repositories.place_repository import PlaceRepository
from app.repositories.trip_repository import TripRepository
from app.services.place_service import PlaceService
from app.services.tour_service import TourService
from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
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
    
    @singleton
    @provider
    def provide_trip_repository(self, db: ElasticsearchClient) -> TripRepository:
        return TripRepository(db)

    #Service
    @singleton
    @provider
    def provide_place_service(self, 
                            place_repository: PlaceRepository,
                            embedding_service: EmbeddingService,
                            openai_service: OpenAIService) -> PlaceService:
        return PlaceService(place_repository, 
                            embedding_service,
                            openai_service)
    
    @singleton
    @provider
    def provide_tour_service(self,
                            place_repository: PlaceRepository,
                            trip_repository: TripRepository,
                            embedding_service: EmbeddingService,
                            openai_service: OpenAIService,
                            distance_matrix_service: DistanceMatrixService
                            ) -> TourService:
        return TourService(
                            place_repository,
                            trip_repository,
                            embedding_service,
                            openai_service,
                            distance_matrix_service)
    
    @singleton
    @provider
    def provide_embedding_service(self) -> EmbeddingService:
        return EmbeddingService(Config.EMBEDDING_MODEL_NAME)
    
    # @singleton
    # @provider
    # def provide_rerank_service(self) -> RerankerService:
    #     return RerankerService(Config.RERANK_MODEL_NAME)
        
    @singleton
    @provider
    def provide_distance_matrix_service(self, place_service: PlaceService) -> DistanceMatrixService:
        return DistanceMatrixService(Config.MAPBOX_API_KEY, place_service)
    
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
    
    @singleton
    @provider
    def provide_distance_time_controller(self, distance_matrix_service: DistanceMatrixService) -> DistanceTimeController:
        return DistanceTimeController(distance_matrix_service)


def configure(binder):
    binder.install(MainModule())
