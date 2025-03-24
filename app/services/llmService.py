from app.models.LLMModel import GPTModel
from injector import inject

class GPTService:
    @inject
    def __init__(self, gpt_model: GPTModel):
        self.gpt_model = gpt_model

    def ask_question(self, prompt):
        return self.gpt_model.ask_gpt(prompt)

    def get_all_logs(self):
        return self.gpt_model.get_logs()

    def get_single_log(self, log_id):
        return self.gpt_model.get_log(log_id)

    def delete_log(self, log_id):
        return self.gpt_model.delete_log(log_id)
