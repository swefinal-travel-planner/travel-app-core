from injector import Module, singleton, provider
from app.services.llmService import GPTService
from app.controllers.llmController import GPTController
from app.models.LLMModel import GPTModel
from config.config import Config

class LLMModule(Module):
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
