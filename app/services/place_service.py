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
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
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

    def embed_text(self, text):
        return self.__embedding_service.embed_text(text)
    
    def get_distance_matrix(self, origin_places, destination_places):
        origins = [f"{lng},{lat}" for lat, lng in origin_places]
        destinations = [f"{lng},{lat}" for lat, lng in destination_places]
        return self.__distance_matrix_service.calculate_distance_matrix(origins, destinations)
    
    def insert_places(self, data):
        list_data = self.parse_mockdata_and_remove_esixts(data)
        if isinstance(list_data, Exception):
            raise ValidationError(f"Error parsing data: {list_data}")
        status = self.process_locations_with_threads(list_data)
        if isinstance(status, Exception):
            raise AppException(f"Error occurred during insertion: {status}")
        return status

    def parse_mockdata_and_remove_esixts(self, data):
        parsed_locations = []
        for feature in data:
            place_id = feature["properties"]["place_id"]
            # Check if the location already exists in the database
            if self.__place_repository.get_place_by_id(place_id) is not None:
                print(f"Location with ID {place_id} already exists. Skipping...")
            else:
                parsed_locations.append(
                    Location(
                        id=place_id,
                        type=feature["type"],
                        properties=feature["properties"],
                        geometry=feature["geometry"]
                    )
                )
                print(f"Location with ID {place_id} does not exist. Adding...")
        return parsed_locations
        
    def convert_raw_location_to_place_by_llm(self, locations) -> Place_list:
        prompt = prompts.convert_location_to_place_prompt
        data = "Đây là danh sách địa điểm: " + ''.join(str(location.to_str()) for location in locations) + '\n'
        label = "Đây là danh sách label " + LABEL
        return self.__openai_service.ask_question(prompt + data + label, Place_list)

    def process_locations_with_threads(self, locations):
        def worker(chunk, stop_processing):
            try:
                listPlace = self.convert_raw_location_to_place_by_llm(chunk)
                if not isinstance(listPlace, Place_list) or not hasattr(listPlace, 'places'):
                    stop_processing.set()

                for place in listPlace.places:
                    if stop_processing.is_set():
                        return None
                    vectorData = self.embed_text(str(place.to_dict()))
                    self.__place_repository.insert_place(place, vectorData)
            except Exception as e:
                stop_processing.set()
                raise AppException(f"{e}")

        chunk_size = 10
        it = iter(locations)
        stop_processing = threading.Event()
        delay_between_requests = 10  # seconds (to respect TPM)

        with ThreadPoolExecutor(max_workers=1) as executor:  # max 1 to ensure spacing
            futures = []
            while True:
                chunk = list(islice(it, chunk_size))
                if not chunk or stop_processing.is_set():
                    break
                futures.append(executor.submit(worker, chunk, stop_processing))
                time.sleep(delay_between_requests)  # spacing request to avoid rate limit

            for future in as_completed(futures):
                if future.exception():
                    raise AppException(f"Error during processing: {future.exception()}")

    def get_place_by_id(self):
        existing_doc = self.__place_repository.get_place_by_id(801950766)
        print(existing_doc)
        # if not existing_doc:
        #     raise NotFoundError(f"No document found with ID '801950766'")
        return existing_doc
        
    def delete_place(self):
        status = self.__place_repository.delete_place(846924729)
        if not status:
            raise NotFoundError(f"Place with ID '846924729' not found")
        return True
    
    def health_check_elastic(self):
        return self.__place_repository.health_check_elastic()
    
    def search_places_after(self, limit, search_after_id, location, language, filter):
        if search_after_id:
            if self.__place_repository.get_place_by_id(search_after_id) is None:
                raise NotFoundError(f"Place after id: '{search_after_id}' not found")
        places = self.__place_repository.search_places_after(limit, search_after_id, location, language, filter)
        # Trả về mảng rỗng nếu không có địa điểm
        return places if places else []