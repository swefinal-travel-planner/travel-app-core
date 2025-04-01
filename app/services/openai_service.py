from openai import OpenAI
from injector import inject
from app.models.place import Place

class OpenAIService:
    @inject
    def __init__(self, api_key: str, model: str):
        self.__api_key = api_key 
        self.__model = model
        self.__client = OpenAI(api_key=self.__api_key)
        print(f"OpenAIService initialized with model '{self.__model}'")

    def ask_question(self, prompt, response_format: type): 
        try:
            response = self.__client.beta.chat.completions.parse(
                model=self.__model,
                messages=[{"role": "developer", "content": "Bạn là một trợ lý về du lịch, chuyên gợi ý và và đánh giá về các địa điểm du lịch"},
                    {"role": "user", "content": prompt}],
                response_format=response_format,
            )

            if response.choices[0].message.refusal:
                print("Refusal: ", response.choices[0].message.refusal)
                return None
            else:
                return response.choices[0].message.parsed
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error interacting with OpenAI API: {e}")
            return None
