from injector import Module, singleton, provider
from app.controllers.place_controller import PlaceController
from app.database.elasticsearch import ElasticsearchClient
from app.repositories.place_repository import PlaceRepository
from app.services.llmService import GPTService
from app.controllers.llmController import GPTController
from app.models.LLMModel import GPTModel
from app.services.place_service import PlaceService
from config.config import Config

class LLMModule(Module):
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
    def provide_place_service(self, place_repository: PlaceRepository) -> PlaceService:
        return PlaceService(place_repository)
    
    #Controller
    @singleton
    @provider
    def provide_place_controller(self, place_service: PlaceService) -> PlaceController:
        return PlaceController(place_service)
    @singleton
    @provider
    def provide_gpt_service(self) -> GPTService:
        return GPTService(GPTModel(api_key=Config.OPENAI_API_KEY, model_name=Config.MODEL_NAME))

    @singleton
    @provider
    def provide_gpt_controller(self, gpt_service: GPTService) -> GPTController:
        return GPTController(gpt_service)

def configure(binder):
    binder.install(LLMModule())
