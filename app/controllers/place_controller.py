from flask import json, jsonify, request
from app.services.place_service import PlaceService
from injector import inject
from app.exceptions.custom_exceptions import AppException, ValidationError, NotFoundError

class PlaceController:
    @inject
    def __init__(self, place_service: PlaceService):
        self.__place_service = place_service

    def get_places(self):
        data = self.__place_service.embed_text('Hello World')
        return str(data)
    
    def get_distance_matrix(self):
        origin_places = [[10.797162181179663, 106.6733851910843]]
        destination_places = [[10.848381955148074, 106.61414722985516], [10.801725010158977, 106.60679246680516]]
        
        # Convert arrays to "longitude,latitude" strings
        origins = [f"{lng},{lat}" for lat, lng in origin_places]
        destinations = [f"{lng},{lat}" for lat, lng in destination_places]
        
        data = self.__place_service.get_distance_matrix(origins, destinations)
        return jsonify(data)
    
    def insert_places(self):
        try:
            if "file" not in request.files:
                raise ValidationError("No file part")
            
            file = request.files["file"]
            if file.filename == "":
                raise ValidationError("No selected file")
            
            if file and file.filename.endswith(".json"):
                data = json.load(file)
                self.__place_service.insert_places(data)
                return jsonify({"status": 200, "message": "Inserted places successfully."}), 200
            else:
                raise ValidationError("Invalid file format. Only JSON files are allowed.")
        except AppException as e:
            return jsonify({"status": e.status_code, "message": e.message}), e.status_code
        except Exception as e:
            return jsonify({"status": 500, "message": f"Unexpected error: {str(e)}"}), 500

    def ask_openai(self):
        response = self.__place_service.ask_question("hello")
        return jsonify(response.model_dump()), 200
    
    def get_places_by_id(self):
        try:
            response = self.__place_service.get_place_by_id()
            return jsonify({"status": 200, "data": str(response)})
        except AppException as e:
            return jsonify({"status": e.status_code, "message": e.message, "details": e.details}), e.status_code

    def delete_place(self):
        try:
            self.__place_service.delete_place()
            return jsonify({"status": 200, "message": "Deleted place successfully."}), 200
        except AppException as e:
            return jsonify({"status": e.status_code, "message": e.message, "details": e.details}), e.status_code