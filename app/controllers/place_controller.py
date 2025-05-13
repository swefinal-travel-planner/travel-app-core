from flask import json, jsonify, request
from app.services.place_service import PlaceService
from injector import inject
from app.models.language import Language
from app.exceptions.custom_exceptions import AppException, ValidationError

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
            if "files" not in request.files:
                raise ValidationError("No files part")
            
            files = request.files.getlist("files")
            if not files:
                raise ValidationError("No selected files")
            
            for file in files:
                if file.filename == "":
                    raise ValidationError("One of the files has no filename")
                
                if file and file.filename.endswith(".json"):
                    data = json.load(file)
                    self.__place_service.insert_places(data)
                else:
                    raise ValidationError(f"Invalid file format for file {file.filename}. Only JSON files are allowed.")
            
            return jsonify({"status": 200, "message": "Inserted places successfully."}), 200
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
            return jsonify({"status": e.status_code, "message": e.message}), e.status_code

    def delete_place(self):
        try:
            self.__place_service.delete_place()
            return jsonify({"status": 200, "message": "Deleted place successfully."}), 200
        except AppException as e:
            return jsonify({"status": e.status_code, "message": e.message}), e.status_code
        
    def check_health_elastic(self):
        try:
            response = self.__place_service.health_check_elastic()
            return jsonify({"status": 200, "message": response}), 200
        except Exception as e:
            return jsonify({"status": 500, "message": f"Elastic search is not healthy: {str(e)}"}), 500
        
    def search_places_after(self):
        """
        Get a list of places with search_after pagination
        ---
        tags:
          - Place
        parameters:
          - name: limit
            in: query
            type: integer
            required: true
          - name: location
            in: query
            type: string
            required: true
          - name: language
            in: query
            type: string
            enum: [en, vi]
            required: true
          - name: filter
            in: query
            type: string
            required: false
          - name: search_after_id
            in: query
            type: string
            required: false
        responses:
          200:
            description: A list of places
            type: object
            schema:
              properties:
                status:
                  type: integer
                  description: The status code of the response
                data:
                  type: array
                  items:
                    type: object
                    description: The list of places

          400:
            description: Validation error
            type: object
            schema:
              properties:
                status:
                  type: integer
                  description: The status code of the response
                message:
                  type: string
                  description: The error message
          500:
            description: Unexpected error
            type: object
            schema:
              properties:
                status:
                  type: integer
                  description: The status code of the response
                message:
                  type: string
                  description: The error message
        """
        try:
            # Validate required parameters
            required_params = ["limit", "location", "language"]
            missing_params = [param for param in required_params if param not in request.args]
            if missing_params:
                raise ValidationError(f"Missing required parameters: {', '.join(missing_params)}")
            
            # Extract parameters
            limit = int(request.args.get("limit"))
            search_after_id = request.args.get("search_after_id") if request.args.get("search_after_id") else None
            location = request.args.get("location")
            language = Language(request.args.get("language"))
            filter = request.args.get("filter") if request.args.get("filter") else None

            # Call the service layer
            response = self.__place_service.search_places_after(limit, search_after_id, location, language, filter)
            return jsonify({"status": 200, "data": response}), 200
        except ValidationError as e:
            return jsonify({"status": 400, "message": e.message}), 400
        except AppException as e:
            return jsonify({"status": e.status_code, "message": e.message}), e.status_code
        except Exception as e:
            return jsonify({"status": 500, "message": f"Unexpected error: {str(e)}"}), 500
