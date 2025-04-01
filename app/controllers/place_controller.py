from flask import json, jsonify, request
from app.services.place_service import PlaceService
from injector import inject

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
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        if file and file.filename.endswith(".json"):
            # Read JSON data
            data = json.load(file)
            response = self.__place_service.insert_places(data)
            print(response)
            #get the last inserted place
            return "Inserted places successfully.", 200
        else:
            return jsonify({"error": "Invalid file format. Only JSON files are allowed."}), 400

    def ask_openai(self):
        response = self.__place_service.ask_question("hello")
        return jsonify(response.model_dump()), 200