import openai


class GPTModel:
    def __init__(self, api_key, model_name):
        openai.api_key = api_key
        self.model_name = model_name
        self.logs = []  # Lưu log request và response

    def ask_gpt(self, prompt):
        """Gọi API OpenAI"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
            result = response['choices'][0]['message']['content']
            self.save_log(prompt, result)
            return result
        except Exception as e:
            return str(e)

    def save_log(self, prompt, response):
        """Lưu log request và response"""
        self.logs.append({"prompt": prompt, "response": response})

    def get_logs(self):
        """Lấy toàn bộ logs"""
        return self.logs

    def get_log(self, log_id):
        """Lấy log theo ID"""
        if 0 <= log_id < len(self.logs):
            return self.logs[log_id]
        return None

    def delete_log(self, log_id):
        """Xóa log theo ID"""
        if 0 <= log_id < len(self.logs):
            return self.logs.pop(log_id)
        return None
