from flask import Blueprint
from injector import Injector
from app.controllers.llmController import GPTController
from di.di_container import configure

api = Blueprint("api", __name__)

# Injector lấy instance đã được đăng ký
injector = Injector(configure)
gpt_controller = injector.get(GPTController)

# Đăng ký routes
api.route("/ask", methods=["POST"])(gpt_controller.ask)
api.route("/logs", methods=["GET"])(gpt_controller.get_logs)
api.route("/logs/<int:log_id>", methods=["GET"])(gpt_controller.get_log)
api.route("/logs/<int:log_id>", methods=["DELETE"])(gpt_controller.delete_log)
