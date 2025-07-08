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
  
  def get_place_by_id(self, place_id):
      """
      Get a place by its ID
      ---
      tags:
        - Place
      parameters:
        - name: Authorization
          in: header
          type: string
          required: true
        - name: place_id
          in: path
          type: string
          required: true
        - name: language
          in: query
          type: string
          enum: [en, vi]
          required: true
      responses:
        200:
          description: Place found
          type: object
          schema:
            properties:
              status:
                type: integer
              data:
                type: object
        400:
          description: Validation error
          type: object
          schema:
            properties:
              status:
                type: integer
              message:
                type: string
        404:
          description: Not found
          type: object
          schema:
            properties:
              status:
                type: integer
              message:
                type: string
        500:
          description: Unexpected error
          type: object
          schema:
            properties:
              status:
                type: integer
              message:
                type: string
      """
      try:
          language_str = request.args.get("language")
          if not language_str:
              raise ValidationError("Missing required parameter: language")
          try:
              language = Language(language_str)
          except ValueError:
              raise ValidationError(f"Invalid language value: '{language_str}'. Must be one of: {[l.value for l in Language]}")
          place = self.__place_service.get_place_by_id(str(place_id), language)
          return jsonify({"status": 200, "data": place}), 200
      except ValidationError as e:
          return jsonify({"status": 400, "message": e.message}), 400
      except AppException as e:
          return jsonify({"status": e.status_code, "message": e.message}), e.status_code
      except Exception as e:
          return jsonify({"status": 500, "message": f"Unexpected error: {str(e)}"}), 500

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
        - name: Authorization
          in: header
          type: string
          required: true
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
        - name: search_keyword
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
          language_str = request.args.get("language")
          # Validate language enum
          try:
              language = Language(language_str)
          except ValueError:
              raise ValidationError(f"Invalid language value: '{language_str}'. Must be one of: {[l.value for l in Language]}")
          filter = request.args.get("filter") if request.args.get("filter") else None
          search_keyword = request.args.get("search_keyword") if request.args.get("search_keyword") else None

          # Call the service layer
          response = self.__place_service.search_places_after(limit, search_after_id, location, language, filter, search_keyword)
          return jsonify({"status": 200, "data": response}), 200
      except ValidationError as e:
          return jsonify({"status": 400, "message": e.message}), 400
      except AppException as e:
          return jsonify({"status": e.status_code, "message": e.message}), e.status_code
      except Exception as e:
          return jsonify({"status": 500, "message": f"Unexpected error: {str(e)}"}), 500
      
  def get_places_in_patch_by_ids(self):
        """
        Get a list of places by IDs in a patch
        ---
        tags:
          - Place
        parameters:
          - name: Authorization
            in: header
            type: string
            required: true
          - name: language
            in: query
            type: string
            enum: [en, vi]
            required: true
          - name: place_ids
            in: query
            type: string
            required: true
            description: A string of place IDs separated by ';'
            example: "id1;id2;id3"
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
                  type: object
                  properties:
                    places:
                      type: array
                      items:
                        type: object
                        description: The list of places
                    not_found_ids:
                      type: array
                      items:
                        type: string
                        description: List of IDs that were not found in the database  

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
            required_params = ["language", "place_ids"]
            missing_params = [param for param in required_params if param not in request.args or not request.args.get(param)]
            if missing_params:
                raise ValidationError(f"Missing required parameter(s): {', '.join(missing_params)}")

            language_str = request.args.get("language")
            place_ids = request.args.get("place_ids")

            # Validate language enum
            try:
                language = Language(language_str)
            except ValueError:
                raise ValidationError(f"Invalid language value: '{language_str}'. Must be one of: {[l.value for l in Language]}")

            response = self.__place_service.search_places_in_patch_by_ids(language, place_ids)
            return jsonify({"status": 200, "data": response}), 200

        except ValidationError as e:
            return jsonify({"status": 400, "message": e.message}), 400
        except AppException as e:
            return jsonify({"status": e.status_code, "message": e.message}), e.status_code
        except Exception as e:
            return jsonify({"status": 500, "message": f"Unexpected error: {str(e)}"}), 500

  def get_random_places(self):
        """
        Get a list of random places
        ---
        tags:
          - Place
        parameters:
          - name: Authorization
            in: header
            type: string
            required: true
          - name: language
            in: query
            type: string
            enum: [en, vi]
            required: true
          - name: limit
            in: query
            type: integer
            required: true
        responses:
          200:
            description: A list of random places
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
                    description: The list of random places

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
            required_params = ["language", "limit"]
            missing_params = [param for param in required_params if param not in request.args or not request.args.get(param)]
            if missing_params:
                raise ValidationError(f"Missing required parameter(s): {', '.join(missing_params)}")

            language_str = request.args.get("language")
            limit = int(request.args.get("limit"))
            long = request.args.get("long")
            lat = request.args.get("lat")
            # Validate language enum
            try:
                language = Language(language_str)
            except ValueError:
                raise ValidationError(f"Invalid language value: '{language_str}'. Must be one of: {[l.value for l in Language]}")

            response = self.__place_service.get_places_randomly(language, limit, long, lat)
            return jsonify({"status": 200, "data": response}), 200

        except ValidationError as e:
            return jsonify({"status": 400, "message": e.message}), 400
        except AppException as e:
            return jsonify({"status": e.status_code, "message": e.message}), e.status_code
        except Exception as e:
            return jsonify({"status": 500, "message": f"Unexpected error: {str(e)}"}), 500
