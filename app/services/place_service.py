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
        try:
            return self.__embedding_service.embed_text(text)
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error embedding text: {e}")
            return None
    
    def get_distance_matrix(self, origin_places, destination_places):
        try:
            origins = [f"{lng},{lat}" for lat, lng in origin_places]
            destinations = [f"{lng},{lat}" for lat, lng in destination_places]
            return self.__distance_matrix_service.calculate_distance_matrix(origins, destinations)
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error calculating distance matrix: {e}")
            return None
    
    def insert_places(self, data):
        try:
            # Convert JSON data to Python object
            list_data = self.parse_mockdata(data)
            self.process_locations_with_threads(list_data)  # Process locations with threading
            # print(f"Inserted {len(list_data)} places successfully.")
            
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error inserting places: {e}")
            return e

    def parse_mockdata(self, data):
        try:
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
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error parsing mock data: {e}")
            return e
        
    def convert_raw_location_to_place_by_llm(self, locations)-> Place_list:
        try:
            prompt = prompts.convert_location_to_place_prompt
            data = "Đây là danh sách địa điểm: " + '.'.join(str(location.to_dict()) for location in locations) + '\n'
            label = "Đây là danh sách label " + LABEL
            return self.__openai_service.ask_question(prompt + data + label, Place_list)
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error asking question: {e}")
            return e

    def process_locations_with_threads(self, locations):
        def worker(chunk):
            inserted_places = []  # Track successfully inserted places for rollback
            try:
                with self.api_semaphore:  # Acquire semaphore to limit concurrent calls
                    time.sleep(self.api_delay)  # Delay to comply with rate limit
                    listPlace = self.convert_raw_location_to_place_by_llm(chunk)
                    #print(listPlace.places[0].to_dict())
                    for place in listPlace.places:
                        vectorData = self.embed_text(str(place.to_dict()))
                        insertStatus = self.__place_repository.insert_place(place, vectorData)
                        if insertStatus != 1 and insertStatus is not Exception:
                            inserted_places.append(place)  # Track successful insert
                            print(f"Inserted place with ID: {place.id}")
                        else:
                            raise Exception(f"Insert failed for place ID: {place.id}")  # Trigger rollback
            except Exception as e:
                # Rollback all successfully inserted places
                # for place in inserted_places:
                #     self.__place_repository.delete_place(place.id)  # Assume delete_place method exists
                #     print(f"Rolled back place with ID: {place.id}")
                print(f"Error in worker: {e}")
                return e

        try:
            threads = []
            chunk_size = 5
            it = iter(locations)

            while True:
                chunk = list(islice(it, chunk_size))
                if not chunk:
                    break
                thread = threading.Thread(target=worker, args=(chunk,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error processing locations with threads: {e}")
            return e
