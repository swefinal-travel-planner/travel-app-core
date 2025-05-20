from flask import Blueprint, request
from injector import Injector
from app.controllers.place_controller import PlaceController
from app.controllers.tour_controller import TourController
from di.di_container import configure
from utils.jwt_auth import jwt_required
from utils.jwt_verify import generate_token
from config.config import Config

api = Blueprint("api", __name__)

injector = Injector(configure)
place_controller = injector.get(PlaceController)
tour_controller = injector.get(TourController)

@api.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.
    ---
    tags:
      - health
    responses:
      200:
        description: Service is up and running
        schema:
          type: object
          properties:
            status:
              type: string
              description: Health status
      500:
        description: Service is down
        schema:
          type: object
          properties:
            status:
              type: string
              description: Health status
    """
    return {"status": "ok"}, 200
api.route("/health-elastic", methods=["POST"])(place_controller.check_health_elastic)

# api for Place controllers

api.route("/places", methods=["GET"])(jwt_required(place_controller.search_places_after))
api.route("/distance_matrix", methods=["GET"])(place_controller.get_distance_matrix)
api.route("/places/insert_data", methods=["POST"])(place_controller.insert_places)
api.route("/ask_openai", methods=["GET"])(place_controller.ask_openai)
api.route("/places/test_get_document", methods=["GET"])(place_controller.get_places_by_id)
api.route("/places/test_delete_document", methods=["DELETE"])(place_controller.delete_place)

#api for Tour controllers
api.route("/tours/create_tour", methods=["POST"])(jwt_required(tour_controller.create_tour))

@api.route("/auth/generate_token", methods=["POST"])
def generate_token_controller():
    """
    Generate a JWT token for authentication in 5 minutes.
    ---
    tags:
      - auths
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            secret_key:
              type: string
              description: The secret key for authentication
    responses:
      200:
        description: JWT token
        schema:
          type: object
          properties:
            token:
              type: string
              description: The generated JWT token
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            status:
              type: integer
              description: Status code
            message:
              type: string
              description: Error message
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            status:
              type: integer
              description: Status code
            message:
              type: string
              description: Error message
    """
    data = request.get_json()
    if not data or "secret_key" not in data:
        return {"status": 400, "message": "Missing secret key"}, 400
    secret_key = data["secret_key"]
    if secret_key != Config.SECRET_KEY:
        return {"status": 401, "message": "Unauthorized"}, 401
    
    token = generate_token({"role": "ADMIN"}, 300)  # Token valid for 5 minutes
    return {"token": token}, 200
# api.route("/places/<int:place_id>", methods=["GET"])(place_controller.get_place)
# api.route("/places/<int:place_id>", methods=["PUT"])(place_controller.update_place)
# api.route("/places/<int:place_id>", methods=["DELETE"])(place_controller.delete_place)
# api.route("/places", methods=["POST"])(place_controller.create_place)