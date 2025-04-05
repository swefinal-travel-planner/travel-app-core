from flask import json
from app.repositories.place_repository import PlaceRepository
from app.services.embedding_service import EmbeddingService
from app.services.distance_matrix_service import DistanceMatrixService
from app.services.openai_service import OpenAIService
from app.models.location import Location
from injector import inject
import constant.prompt as prompts
from constant.label import LABEL
from app.models.place import Place_list, Place
import threading
from itertools import islice
import time
from threading import Semaphore
from app.exceptions.custom_exceptions import AppException,ValidationError, NotFoundError

class PlaceService:
    @inject
    def __init__(self,
                  place_repository: PlaceRepository,
                  embedding_service: EmbeddingService,
                  distance_matrix_service: DistanceMatrixService,
                  openai_service: OpenAIService):
        self.__place_repository = place_repository
        self.__embedding_service = embedding_service
        self.__distance_matrix_service = distance_matrix_service
        self.__openai_service = openai_service

    # Semaphore to limit concurrent API calls
    api_semaphore = Semaphore(5)  # Allow up to 5 threads to call the API concurrently
    api_delay = 60 / 300  # Delay to ensure 300 requests per minute (0.2 seconds per request)

    def embed_text(self, text):
        return self.__embedding_service.embed_text(text)
    
    def get_distance_matrix(self, origin_places, destination_places):
        origins = [f"{lng},{lat}" for lat, lng in origin_places]
        destinations = [f"{lng},{lat}" for lat, lng in destination_places]
        return self.__distance_matrix_service.calculate_distance_matrix(origins, destinations)
    
    def insert_places(self, data):
        list_data = self.parse_mockdata(data)
        if isinstance(list_data, Exception):
            raise ValidationError(f"Error parsing data: {list_data}")
        status = self.process_locations_with_threads(list_data)
        if isinstance(status, Exception):
            raise AppException(f"Error occurred during insertion: {status}")
        return status

    def parse_mockdata(self, data):
        features = data.get("features", [])
        return [
            Location(
                id=feature["properties"]["datasource"]["raw"]["osm_id"],
                type=feature["type"],
                properties=feature["properties"],
                geometry=feature["geometry"]
            )
            for feature in features
        ]
        
    def convert_raw_location_to_place_by_llm(self, locations) -> Place_list:
        prompt = prompts.convert_location_to_place_prompt
        data = "Đây là danh sách địa điểm: " + '.'.join(str(location.to_dict()) for location in locations) + '\n'
        label = "Đây là danh sách label " + LABEL
        return self.__openai_service.ask_question(prompt + data + label, Place_list)

    def process_locations_with_threads(self, locations):
        def worker(chunk, result):
            inserted_places = []  # Track successfully inserted places for rollback
            try:
                with self.api_semaphore:  # Acquire semaphore to limit concurrent calls
                    time.sleep(self.api_delay)  # Delay to comply with rate limit
                    listPlace = self.convert_raw_location_to_place_by_llm(chunk)
                    for place in listPlace.places:
                        vectorData = self.embed_text(str(place.to_dict()))
                        insertStatus = self.__place_repository.insert_place(place, vectorData)
                        if insertStatus:
                            inserted_places.append(place.id)  # Track successful insert
            except Exception as e:
                # Rollback in case of failure
                for inserted_id in inserted_places:
                    self.__place_repository.delete_place(inserted_id)
                result["error"] = e  # Store the exception in the shared result
            finally:
                result["done"] = True  # Mark the thread as done

        threads = []
        chunk_size = 5
        it = iter(locations)
        results = []

        while True:
            chunk = list(islice(it, chunk_size))
            if not chunk:
                break
            result = {"done": False, "error": None}
            results.append(result)
            thread = threading.Thread(target=worker, args=(chunk, result))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Check for errors in any thread
        for result in results:
            if result["error"]:
                raise AppException(f"Error processing locations: {result['error']}")

    def get_place_by_id(self):
        existing_doc = self.__place_repository.get_place_by_id(801950766)
        if not existing_doc:
            raise NotFoundError(f"No document found with ID '801950766'")
        return existing_doc
        
    def delete_place(self):
        status = self.__place_repository.delete_place(846924729)
        if not status:
            raise NotFoundError(f"Place with ID '846924729' not found")
        return True