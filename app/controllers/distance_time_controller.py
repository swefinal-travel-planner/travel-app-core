from flask import request
from app.services.distance_matrix_service import DistanceMatrixService
from app.exceptions.custom_exceptions import AppException,ValidationError, NotFoundError


class DistanceTimeController:
    def __init__(self, distance_matrix_service: DistanceMatrixService):
        self.distance_matrix_service = distance_matrix_service

    def get_distance_time(self):
        """
        Get the distance and time between a list of place IDs.
        ---
        tags:
            - Distance and Time
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
                  place_ids:
                    type: array
                    items:
                      type: string
                    description: List of place IDs to calculate distance and time for.
        responses:
            200:
              description: Distance and time successfully calculated.
              type: object
              schema:
                properties:
                    status:
                      type: integer
                      description: The status code of the response.
                    data:
                      type: array
                      items:
                        type: object
                        properties:
                            source_id:
                              type: string
                              description: The source place ID.
                            destination_id:
                              type: string
                              description: The destination place ID.
                            distance:
                              type: number
                              description: The distance between the two places in kilometers.
                            time:
                              type: number
                              description: The travel time between the two places in minutes.
                        
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
            if not data or 'place_ids' not in data:
                return {"status": 400, "message": "Invalid input data"}, 400
            place_ids = data['place_ids']
            if not isinstance(place_ids, list) or len(place_ids) < 2:
                return {"status": 400, "message": "At least two place IDs are required"}, 400
            if not all(isinstance(pid, str) for pid in place_ids):
                return {"status": 400, "message": "All place IDs must be strings"}, 400
            distances = self.distance_matrix_service.get_distance_time(place_ids)
            return {"status": 200, "data": distances}, 200
        except Exception as e:
            if isinstance(e, ValueError):
                return {"status": 400, "message": str(e)}, 400
            elif isinstance(e, NotFoundError):
                return {"status": 404, "message": e.message}, 404
            return {"status": 500, "message": str(e)}, 500