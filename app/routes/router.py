from flask import Blueprint
from injector import Injector
from app.controllers.place_controller import PlaceController
from di.di_container import configure

api = Blueprint("api", __name__)

injector = Injector(configure)
place_controller = injector.get(PlaceController)

# api for Place controllers

api.route("/places", methods=["GET"])(place_controller.get_places)
api.route("/distance_matrix", methods=["GET"])(place_controller.get_distance_matrix)
api.route("/places/insert_data", methods=["POST"])(place_controller.insert_places)
api.route("/ask_openai", methods=["GET"])(place_controller.ask_openai)
# api.route("/places/<int:place_id>", methods=["GET"])(place_controller.get_place)
# api.route("/places/<int:place_id>", methods=["PUT"])(place_controller.update_place)
# api.route("/places/<int:place_id>", methods=["DELETE"])(place_controller.delete_place)
# api.route("/places", methods=["POST"])(place_controller.create_place)