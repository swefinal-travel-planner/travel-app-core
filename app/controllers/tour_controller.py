from injector import inject
from app.services.tour_service import TourService
from flask import jsonify, request
from app.exceptions.custom_exceptions import AppException, ValidationError
from app.models.user_references_request import UserReferencesRequest
from app.models.location_preference import LocationPreference

class TourController:
    @inject
    def __init__(self, tour_service:TourService):
        self.tour_service = tour_service

    def create_tour(self):
        """
        Create a tour based on user preferences.
        ---
        tags:
        - Tour
        parameters:
        - name: Authorization
          in: header
          required: true
          type: string
        - name: body
          in: body
          required: true
          type: json
          schema:
            type: object
            properties:
              city:
                type: string
                description: The city to create a tour in
              days:
                type: integer
                description: The number of days for the tour (1-7)
              locationsPerDay:
                type: integer
                description: The number of locations per day (5-9)
              location_attributes:
                type: array
                items:
                  type: string
                  description: The location attributes to consider
              food_attributes:
                type: array
                items:
                  type: string
                  description: The food attributes to consider
              special_requirements:
                type: array
                items:
                  type: string
                  description: Special requirements for the tour
              medical_conditions:
                type: array
                items:
                  type: string
                  description: Medical conditions to consider
              locationPreference:
                type: string
                enum: ["proximity", "relevance", "balanced"]
                description: The location preference for the tour
        responses:
          200:
            description: The product inserted in the database
            type: object
            schema:
              properties:
                status:
                  type: integer
                  description: The status code of the response
                data:
                  type: object
                  properties:
                    reference_id:
                      type: string
                      description: The reference ID of the tour
                    trip_items:
                      type: array
                      items:
                        type: object
                        description: The list of trip items
                        properties:
                          trip_day:
                            type: integer
                            description: The day of the trip
                          order_in_day:
                            type: integer
                            description: The order of the location in the day
                          time_in_day:
                            type: string
                            description: The time of the day
                            enum: ["morning", "afternoon", "evening"]
                          place:
                            type: object
                            description: The place details
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
            data = request.get_json()
            if not data:
                raise ValidationError("No data provided")
            
            missing_fields = [key for key in ["city", "days", "locationsPerDay", "location_attributes", "food_attributes", "special_requirements", "medical_conditions", "locationPreference"] if key not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
            
            if not isinstance(data["days"], int) or data["days"] <= 0 or data["days"] > 7:
                raise ValidationError("Days must be a positive integer, between 1 and 7")
            
            if not isinstance(data["locationsPerDay"], int) or data["locationsPerDay"] < 5 or data["locationsPerDay"] > 9:
                raise ValidationError("Locations per day must be a positive integer, between 5 and 9")
            
            if not isinstance(data["location_attributes"], list) or len(data["location_attributes"]) == 0 or not all(isinstance(attr, str) for attr in data["location_attributes"]):
                raise ValidationError("Location attributes must be a list of strings and cannot be empty")
            
            if not isinstance(data["food_attributes"], list) or len(data["food_attributes"]) == 0 or not all(isinstance(attr, str) for attr in data["food_attributes"]):
                raise ValidationError("Food attributes must be a list of strings and cannot be empty")
            
            if not isinstance(data["special_requirements"], list) or len(data["special_requirements"]) == 0 or not all(isinstance(req, str) for req in data["special_requirements"]):
                raise ValidationError("Special requirements must be a list of strings and cannot be empty")
            
            if not isinstance(data["medical_conditions"], list) or len(data["medical_conditions"]) == 0 or not all(isinstance(cond, str) for cond in data["medical_conditions"]):
                raise ValidationError("Medical conditions must be a list of strings and cannot be empty")
            
            try:
                locationPreference = LocationPreference.from_string(data.get("locationPreference"))
            except ValueError:
                raise ValidationError("Invalid location preference. Location preference must be one of 'proximity', 'relevance', or 'balanced'.")

            user_references = UserReferencesRequest(

                city=data.get("city"),
                days=data.get("days"),
                locationsPerDay=data.get("locationsPerDay"),
                location_attributes=data.get("location_attributes"),
                food_attributes=data.get("food_attributes"),
                special_requirements=data.get("special_requirements"),
                medical_conditions=data.get("medical_conditions"),
                locationPreference=LocationPreference.from_string(data.get("locationPreference")).to_string()
            )
            
            tours = self.tour_service.create_tour(user_references)
            return jsonify({"status": 200, "data": tours}), 200  # Return raw list of dictionaries
        except Exception as e:
            return jsonify({"status": 500, "message": f"Unexpected error: {str(e)}"}), 500

    def generate_label_cache(self):
      data = request.get_json()
      user_references = UserReferencesRequest(
        city=data.get("city"),
        days=data.get("days"),
        locationsPerDay=data.get("locationsPerDay"),
        location_attributes=data.get("location_attributes"),
        food_attributes=data.get("food_attributes"),
        special_requirements=data.get("special_requirements"),
        medical_conditions=data.get("medical_conditions"),
        locationPreference=LocationPreference.from_string(data.get("locationPreference")).to_string()
      )

      self.tour_service.cache_labels(user_references)
      return jsonify({"status": 200, "message": "Label cache generated successfully"}), 200