from injector import inject
from app.models.user_references_request import UserReferencesRequest
from app.models.tour_references import TourReferences
from app.services.openai_service import OpenAIService
import constant.prompt as prompts
from constant.label import LABEL

class TourService:
    @inject
    def __init__(self, openai_service: OpenAIService):
        self.__openai_service = openai_service

    def create_tour(self, user_references: UserReferencesRequest):
        #convert user references to tour references in label
        tour_references = self.convert_user_references_to_tour_references(user_references)
        return tour_references
        
    def convert_user_references_to_tour_references(self, user_references: UserReferencesRequest) -> TourReferences:
        prompt = prompts.convert_user_references_to_tour_references_prompt
        data = "Đây là danh sách yêu cầu của người dùng: " + ''.join(str(user_references.to_dict())) + '\n'
        label = "Đây là danh sách các nhãn dán: " + LABEL
        print("Prompt: ", prompt + data + label)
        return self.__openai_service.ask_question(prompt + data + label, TourReferences)