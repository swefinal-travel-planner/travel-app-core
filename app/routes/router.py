from flask import Blueprint
from injector import Injector
from app.controllers.llmController import GPTController
from app.controllers.place_controller import PlaceController
from di.di_container import configure

api = Blueprint("api", __name__)

injector = Injector(configure)
gpt_controller = injector.get(GPTController)
place_controller = injector.get(PlaceController)

# api for LLM controllers
api.route("/ask", methods=["POST"])(gpt_controller.ask)
api.route("/logs", methods=["GET"])(gpt_controller.get_logs)
api.route("/logs/<int:log_id>", methods=["GET"])(gpt_controller.get_log)
api.route("/logs/<int:log_id>", methods=["DELETE"])(gpt_controller.delete_log)

# api for Place controllers

api.route("/places", methods=["GET"])(place_controller.get_places)
# api.route("/places/<int:place_id>", methods=["GET"])(place_controller.get_place)
# api.route("/places/<int:place_id>", methods=["PUT"])(place_controller.update_place)
# api.route("/places/<int:place_id>", methods=["DELETE"])(place_controller.delete_place)
# api.route("/places", methods=["POST"])(place_controller.create_place)