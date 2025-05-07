from openai import OpenAI
from injector import inject

from app.exceptions.custom_exceptions import AppException

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
                messages=[{"role": "developer", "content": "Bạn là một trợ lý về du lịch, luôn trả lời trung thực và chính xác nhất có thể."},
                    {"role": "user", "content": prompt}],
                response_format=response_format,
            )

            if response.choices[0].message.refusal:
                raise AppException(f"Refusal: {response.choices[0].message.refusal}")
            else:
                return response.choices[0].message.parsed
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error interacting with OpenAI API: {e}")
            raise AppException(f"Error interacting with OpenAI API: {e.response.json()['error'].get('message', 'Unknown error')}")
