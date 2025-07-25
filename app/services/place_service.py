from flask import json
from app.repositories.place_repository import PlaceRepository
from app.services.embedding_service import EmbeddingService
from app.services.openai_service import OpenAIService
from app.models.location import Location
from app.models.language import Language
from injector import inject
import constant.prompt as prompts
from constant.label import LABEL
from app.models.place import Place_list
from app.models.place_response import PlaceResponse
import threading
from itertools import islice
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.exceptions.custom_exceptions import AppException,ValidationError, NotFoundError
from utils.extract_id import extract_ids_from_string
from utils.get_location import get_address_by_location, get_district_by_address
import constant.label as label_tools

class PlaceService:
    @inject
    def __init__(self,
                  place_repository: PlaceRepository,
                  embedding_service: EmbeddingService,
                  openai_service: OpenAIService):
        self.__place_repository = place_repository
        self.__embedding_service = embedding_service
        self.__openai_service = openai_service

    def embed_text(self, text):
        return self.__embedding_service.embed_text(text)
    
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
        data = "Here is a list of places: " + ''.join(str(location.to_str()) for location in locations) + '\n'
        label = "Here is the list of labels: " + LABEL
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

    def get_place_by_id(self, place_id: str, language):
        place = self.__place_repository.get_place_by_id(place_id)
        if not place:
            raise NotFoundError(f"No document found with ID '{place_id}'")
        # Chuyển đổi sang PlaceResponse
        return PlaceResponse(
            id=place["id"],
            name=place.get(f"{language.to_string()}_name", ""),
            address=place.get(f"{language.to_string()}_address", ""),
            long=place.get("long"),
            lat=place.get("lat"),
            properties=place.get(f"{language.to_string()}_properties", {}),
            type=place.get(f"{language.to_string()}_type", ""),
            images=place.get("images")
        ).to_dict()

    def delete_place(self, place_id: str):
        status = self.__place_repository.delete_place(place_id)
        if not status:
            raise NotFoundError(f"Place with ID '{place_id}' not found")
        return True
    
    def health_check_elastic(self):
        return self.__place_repository.health_check_elastic()

    def search_places_after(self, limit, search_after_id, location, language, filter, search_keyword):
        if search_after_id:
            if self.__place_repository.get_place_by_id(search_after_id) is None:
                raise NotFoundError(f"Place after id: '{search_after_id}' not found")
        extract_filter = []
        if filter is not None:
            extracter = [x.strip() for x in filter.split(",")]
            if language == Language.EN:
                extract_filter = [label_tools.normalize_label_en(x) for x in extracter]
            elif language == Language.VI:
                extract_filter = [label_tools.normalize_label_vi(x) for x in extracter]
        places = self.__place_repository.search_places_after(limit, search_after_id, location, language, extract_filter, search_keyword)
        # Trả về mảng rỗng nếu không có địa điểm
        if not places:
            return []
        # Chuyển đổi kết quả thành danh sách PlaceResponse
        #---------------------------- --------------------------------------------------
        return [PlaceResponse(
            id=place["id"],
            name=place[f"{language.to_string()}_name"],
            address=place[f"{language.to_string()}_address"],
            long=place["long"],
            lat=place["lat"],
            properties=place[f"{language.to_string()}_properties"],
            type=place[f"{language.to_string()}_type"],
            images=place["images"]
        ).to_dict() for place in places]

    def search_places_in_patch_by_ids(self, language, place_ids: str):

        place_ids = extract_ids_from_string(place_ids)
        if len(place_ids) == 0:
            raise ValidationError("No place IDs provided or invalid format")

        places = self.__place_repository.get_places_in_patch_by_ids(language, place_ids)
        # check if there are some id that not found in database
        if len(places) < len(place_ids):
            found_ids = [place["id"] for place in places]
            not_found_ids = []
            for place_id in place_ids:
                if place_id not in found_ids:
                    not_found_ids.append(place_id)

            # change to PlaceResponse
            found_places = [
                PlaceResponse(
                    id=place["id"],
                    name=place[f"{language.to_string()}_name"],
                    address=place[f"{language.to_string()}_address"],
                    long=place["long"],
                    lat=place["lat"],
                    properties=place[f"{language.to_string()}_properties"],
                    type=place[f"{language.to_string()}_type"],
                    images=place["images"]
                ).to_dict() for place in places
            ]
            return {"places": found_places, "not_found_ids": not_found_ids}

        # Chuyển đổi kết quả thành danh sách PlaceResponse
        return {"places": [PlaceResponse(
            id=place["id"],
            name=place[f"{language.to_string()}_name"],
            address=place[f"{language.to_string()}_address"],  # Assuming address is not provided in the data
            long=place["long"],
            lat=place["lat"],
            properties=place[f"{language.to_string()}_properties"],
            type=place[f"{language.to_string()}_type"],
            images=place["images"]
        ).to_dict() for place in places], "not_found_ids": []}
    
    def get_places_randomly(self, language, limit, long=None, lat=None):
        # Kiểm tra xem long và lat có được cung cấp không
        address = get_address_by_location(long, lat) if long and lat else None
        district = get_district_by_address(address) if address else None

        places = self.__place_repository.get_random_places(language, limit, district=district)
        if not places:
            return []
        # Chuyển đổi kết quả thành danh sách PlaceResponse
        return [PlaceResponse(
            id=place["id"],
            name=place[f"{language.to_string()}_name"],
            address=place[f"{language.to_string()}_address"],  # Assuming address is not provided in the data
            long=place["long"],
            lat=place["lat"],
            properties=place[f"{language.to_string()}_properties"],
            type=place[f"{language.to_string()}_type"],
            images=place["images"]
        ).to_dict() for place in places]