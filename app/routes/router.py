from flask import Blueprint
from injector import Injector
from app.controllers.place_controller import PlaceController
from app.controllers.tour_controller import TourController
from di.di_container import configure

api = Blueprint("api", __name__)

injector = Injector(configure)
place_controller = injector.get(PlaceController)
tour_controller = injector.get(TourController)

@api.route("/health", methods=["GET"])
def health_check():
    return {"status": "ok"}, 200
# api for Place controllers

api.route("/places", methods=["GET"])(place_controller.get_places)
api.route("/distance_matrix", methods=["GET"])(place_controller.get_distance_matrix)
api.route("/places/insert_data", methods=["POST"])(place_controller.insert_places)
api.route("/ask_openai", methods=["GET"])(place_controller.ask_openai)
api.route("/places/test_get_document", methods=["GET"])(place_controller.get_places_by_id)
api.route("/places/test_delete_document", methods=["DELETE"])(place_controller.delete_place)

#api for Tour controllers
api.route("/tours/create_tour", methods=["POST"])(tour_controller.create_tour)
# api.route("/places/<int:place_id>", methods=["GET"])(place_controller.get_place)
# api.route("/places/<int:place_id>", methods=["PUT"])(place_controller.update_place)
# api.route("/places/<int:place_id>", methods=["DELETE"])(place_controller.delete_place)
# api.route("/places", methods=["POST"])(place_controller.create_place)