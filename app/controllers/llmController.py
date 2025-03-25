from flask import request, jsonify
from app.services.llmService import GPTService
from injector import inject

class GPTController:
    @inject
    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service

    def ask(self):
        data = request.json
        prompt = data.get("prompt")

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        response = self.gpt_service.ask_question(prompt)
        return jsonify({"prompt": prompt, "response": response})

    def get_logs(self):
        logs = self.gpt_service.get_all_logs()
        return jsonify({"logs": logs})

    def get_log(self, log_id):
        log = self.gpt_service.get_single_log(log_id)
        if log:
            return jsonify({"log": log})
        return jsonify({"error": "Log not found"}), 404

    def delete_log(self, log_id):
        log = self.gpt_service.delete_log(log_id)
        if log:
            return jsonify({"message": "Log deleted successfully", "log": log})
        return jsonify({"error": "Log not found"}), 404
