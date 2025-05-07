from injector import inject
from app.services.tour_service import TourService
from flask import jsonify, request
from app.exceptions.custom_exceptions import AppException, ValidationError
from app.models.user_references_request import UserReferencesRequest

class TourController:
    @inject
    def __init__(self, tour_service:TourService):
        self.tour_service = tour_service

    def create_tour(self):
        try:
            data = request.get_json()
            if not data:
                raise ValidationError("No data provided")
            
            
            missing_fields = [key for key in ["city", "days", "location_attributes", "food_attributes", "special_requirements", "medical_conditions"] if key not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
            
            if not isinstance(data["days"], int) or data["days"] <= 0 or data["days"] > 7:
                raise ValidationError("Days must be a positive integer, between 1 and 7")
            
            if not isinstance(data["location_attributes"], list) or len(data["location_attributes"]) == 0 or not all(isinstance(attr, str) for attr in data["location_attributes"]):
                raise ValidationError("Location attributes must be a list of strings and cannot be empty")
            
            if not isinstance(data["food_attributes"], list) or len(data["food_attributes"]) == 0 or not all(isinstance(attr, str) for attr in data["food_attributes"]):
                raise ValidationError("Food attributes must be a list of strings and cannot be empty")
            
            if not isinstance(data["special_requirements"], list) or len(data["special_requirements"]) == 0 or not all(isinstance(req, str) for req in data["special_requirements"]):
                raise ValidationError("Special requirements must be a list of strings and cannot be empty")
            
            if not isinstance(data["medical_conditions"], list) or len(data["medical_conditions"]) == 0 or not all(isinstance(cond, str) for cond in data["medical_conditions"]):
                raise ValidationError("Medical conditions must be a list of strings and cannot be empty")
            
            user_references = UserReferencesRequest(

                city=data.get("city"),
                days=data.get("days"),
                location_attributes=data.get("location_attributes"),
                food_attributes=data.get("food_attributes"),
                special_requirements=data.get("special_requirements"),
                medical_conditions=data.get("medical_conditions")
            )
            
            tours = self.tour_service.create_tour(user_references)
            return jsonify({"status": 200, "data": tours}), 200  # Return raw list of dictionaries
        except AppException as e:
            return jsonify({"status": e.status_code, "message": e.message}), e.status_code
        except Exception as e:
            return jsonify({"status": 500, "message": f"Unexpected error: {str(e)}"}), 500
