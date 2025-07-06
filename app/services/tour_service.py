from injector import inject
from app.models.user_references_request import UserReferencesRequest
from app.models.tour_references import TourReferences
from app.models.place_with_score import PlaceWithScore
from app.models.place_with_score_collapse import PlaceWithScoreCollapse,PlaceWithScoreCollapseList
from app.models.place_with_location import PlaceWithLocation
from app.models.trip_item import TripItem, TripItemWithPlace
from app.models.time_in_day import TimeInDay
from app.models.location_preference import LocationPreference
from app.models.trip_item_research import TripItemResearch, TripItemResearchList
from app.repositories.place_repository import PlaceRepository
from app.repositories.trip_repository import TripRepository
from app.services.openai_service import OpenAIService
from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
from app.services.distance_matrix_service import DistanceMatrixService
from app.models.location_labels_extract import LocationLabelsExtract
from app.models.food_labels_extract import FoodLabelsExtract
import constant.prompt as prompts
from constant.label import LABEL
import asyncio
from utils.normalize_label_array import extract_labels_from_string

class TourService:
    @inject
    def __init__(self,
                place_repository: PlaceRepository,
                trip_repository: TripRepository,
                embedding_service: EmbeddingService,
                openai_service: OpenAIService,
                distance_matrix_service: DistanceMatrixService):
        self.__openai_service = openai_service
        self.__place_repository = place_repository
        self.__trip_repository = trip_repository
        self.__embedding_service = embedding_service
        self.__distance_matrix_service = distance_matrix_service

    def create_tour_demo(self, user_references: UserReferencesRequest, neighbor_district: list[str]):
        try:
            TOTAL_LOCATIONS = user_references.days * (user_references.locationsPerDay - 3) * 4
            TOTAL_FOOD_LOCATIONS = user_references.days * 3 * 4
            #convert user references to tour references in label
            #check db to reduce convert time
            tour_references = self.convert_user_references_to_tour_references(user_references)
            print("convert complete")

            #embedding location_attribute_label and food_attribute_label to vector
            location_attributes_label_embedding = self.__embedding_service.embed_text(str(tour_references.en_location_attributes_label) + "," + str(tour_references.vi_location_attributes_label))
            food_attributes_label_embedding = self.__embedding_service.embed_text(str(tour_references.en_food_attributes_label) + "," + str(tour_references.vi_food_attributes_label))
            print("embedding complete")

            #search for places in the database
            tourist_destination_list_parse, food_location_list_parse = self.search_places(TOTAL_LOCATIONS, TOTAL_FOOD_LOCATIONS, tour_references, location_attributes_label_embedding, food_attributes_label_embedding, neighbor_district)

            return [tourist_destination_list_parse + food_location_list_parse]
        except Exception as e:
            print(f"Error creating tour: {e}")
            raise e

    def create_tour(self, user_references: UserReferencesRequest, neighbor_district: list[str]):
        try:
            TOTAL_LOCATIONS = user_references.days * (user_references.locationsPerDay - 3) * 4
            TOTAL_FOOD_LOCATIONS = user_references.days * 3 * 4
            #convert user references to tour references in label
            #check db to reduce convert time
            tour_references = self.convert_user_references_to_tour_references(user_references)
            print("convert complete")

            #embedding location_attribute_label and food_attribute_label to vector
            location_attributes_label_embedding = self.__embedding_service.embed_text(str(tour_references.en_location_attributes_label) + "," + str(tour_references.vi_location_attributes_label))
            food_attributes_label_embedding = self.__embedding_service.embed_text(str(tour_references.en_food_attributes_label) + "," + str(tour_references.vi_food_attributes_label))
            print("embedding complete")

            #search for places in the database
            tourist_destination_list_parse, food_location_list_parse = self.search_places(TOTAL_LOCATIONS, TOTAL_FOOD_LOCATIONS, tour_references, location_attributes_label_embedding, food_attributes_label_embedding, neighbor_district)

            #rerank places by llm
            all_places = tourist_destination_list_parse + food_location_list_parse
            batch_size = 20  # Tune this based on LLM limits and latency
            batches = [all_places[i:i + batch_size] for i in range(0, len(all_places), batch_size)]

            async def rerank_all_batches():
                tasks = [
                    self.rerank_places_by_llm_async(batch, tour_references)
                    for batch in batches
                ]
                results = await asyncio.gather(*tasks)
                # Flatten the list of lists
                return [place for batch in results for place in batch]

            rerank_list = asyncio.run(rerank_all_batches())
            print("rerank by llm complete")

            #split places into tourist destination, breakfast, lunch, dinner
            tourist_destination_list = []
            breakfast_list = []
            lunch_dinner_list = []
            #add to store list
            location_store_list = TripItemResearchList()
            breakfast_store_list = TripItemResearchList()
            lunch_dinner_store_list = TripItemResearchList()
            for place in rerank_list:
                if place.score > 0:
                    if "food location" in place.en_type:
                        if "breakfast" in place.en_type:
                            breakfast_list.append(PlaceWithLocation(
                                id=place.id,
                                score=place.score,
                                lat=place.lat,
                                long=place.long,
                            ))
                            breakfast_store_list.add(TripItemResearch(place_id=place.id, score=place.score, is_selected=False))
                        else:
                            lunch_dinner_list.append(PlaceWithLocation(
                                id=place.id,
                                score=place.score,
                                lat=place.lat,
                                long=place.long,
                            ))
                            lunch_dinner_store_list.add(TripItemResearch(place_id=place.id, score=place.score, is_selected=False))
                    else:
                        tourist_destination_list.append(PlaceWithLocation(
                                id=place.id,
                                score=place.score,
                                lat=place.lat,
                                long=place.long,
                            ))
                        location_store_list.add(TripItemResearch(place_id=place.id, score=place.score, is_selected=False))
            print("split complete")

            #sort places by score
            breakfast_list.sort(key=lambda x: x.score, reverse=True)

            if len(breakfast_list) < tour_references.days:
                raise ValueError("Not enough breakfast places found")
            if len(lunch_dinner_list) < tour_references.days * 2:
                raise ValueError("Not enough lunch/dinner places found")
            if len(tourist_destination_list) < tour_references.days * (tour_references.locationsPerDay - 3):
                raise ValueError("Not enough tourist destination places found")
            
            # Await the async method properly
            asyncio.run(self.process_tour_data(breakfast_list, tourist_destination_list, lunch_dinner_list))
            print("distance matrix complete")

            #generate trip items
            trip_items = self.generate_trip_items(breakfast_list, lunch_dinner_list, tourist_destination_list, tour_references.days, tour_references.locationsPerDay, LocationPreference.from_string(tour_references.locationPreference).to_float())
            print("generate trip items complete")
            
            #add place to trip items
            finalTripItems = []
            for trip_item in trip_items:
                for place in tourist_destination_list_parse + food_location_list_parse:
                    if trip_item.place_id == place.id:
                        finalTripItems.append(TripItemWithPlace(
                            place=place,
                            tripItem=trip_item,
                        ))
                        break
            #store trip to database
            pre_store_trip(trip_items, location_store_list, breakfast_store_list, lunch_dinner_store_list)
            store_id = self.__trip_repository.insert_trip(tour_references, breakfast_store_list, lunch_dinner_store_list, location_store_list)

            return {"reference_id": store_id, "trip_items" :[trip_item.to_dict() for trip_item in trip_items]}
        except Exception as e:
            print(f"Error creating tour: {e}")
            raise e

    def search_places(self, TOTAL_LOCATIONS, TOTAL_FOOD_LOCATIONS, tour_references, location_attributes_label_embedding, food_attributes_label_embedding, neighbor_district):
        city = tour_references.city.split(",")[1].strip()
        #group district and neighbor district
        district_pool = [tour_references.city.split(",")[0].strip()] + neighbor_district
        print(district_pool)
        #search places by vector
        loop_count = 0
        is_enough_locations = False
        is_enough_food_locations = False
        tourist_destination_list_parse = []
        food_location_list_parse = []
        while not (is_enough_locations and is_enough_food_locations):
            if not is_enough_locations:
                locations_places_list = self.__place_repository.search_places_by_vector(location_attributes_label_embedding, TOTAL_LOCATIONS + loop_count, city, district_pool)
            if not is_enough_food_locations:
                food_places_list = self.__place_repository.search_places_by_vector(food_attributes_label_embedding, TOTAL_FOOD_LOCATIONS + loop_count, city, district_pool)
            print("search complete")
            #parse places from es hits and remove duplicates
            tourist_destination_list_parse = parse_places_from_es_hits(locations_places_list)
            food_location_list_parse = parse_places_from_es_hits(food_places_list)
            print("parse complete")

                # Remove places from food_location_listaces that exist in locations_places_list (by id)
            food_place_ids = [hit.id for hit in food_location_list_parse]
            tourist_destination_list_parse = [
                    place for place in tourist_destination_list_parse if place.id not in food_place_ids
                ]
            
            print("remove food places from tourist destination complete")
                #check if there are enough locations and food places
            is_enough_locations = len(tourist_destination_list_parse) >= tour_references.days * (tour_references.locationsPerDay - 3) + loop_count
            is_enough_food_locations = len(food_location_list_parse) >= tour_references.days * 3 + loop_count
            if len([place for place in food_location_list_parse if "breakfast" in place.en_type]) < tour_references.days:
                is_enough_food_locations = False

            if not (is_enough_locations and is_enough_food_locations):
                loop_count += 1
                if not is_enough_locations:
                    print(f"Not enough tourist destinations found. Increasing search limit to {TOTAL_LOCATIONS + loop_count}.")
                if not is_enough_food_locations:
                    print(f"Not enough food places found. Increasing search limit to {TOTAL_FOOD_LOCATIONS + loop_count}.")
                if loop_count > 10:
                    raise ValueError("Not enough locations or food places found. Please adjust your preferences.")
        return tourist_destination_list_parse,food_location_list_parse
        
    def convert_user_references_to_tour_references(self, user_references: UserReferencesRequest) -> TourReferences:
        #check location labels and food labels in cache
        tour_data = TourReferences(city=user_references.city,
                                   days=user_references.days,
                                   locationsPerDay=user_references.locationsPerDay,
                                   location_attributes=user_references.location_attributes,
                                   food_attributes=user_references.food_attributes,
                                   en_location_attributes_label=["location"],
                                   vi_location_attributes_label=["địa điểm"],
                                   en_food_attributes_label=["food"],
                                   vi_food_attributes_label=["món ăn"],
                                   locationPreference=user_references.locationPreference,
                                   special_requirements=user_references.special_requirements,
                                   medical_conditions=user_references.medical_conditions)
        data = self.cache_labels(user_references)

        if data["vi_location_attributes_labels"] == []:
            try:
                prompt = prompts.convert_user_location_references_to_labels_prompt
                location_data_str = "Here is the user's request list for tourist destinations: " + ' '.join(str(user_references.location_attributes_to_str())) + '\n'
                label = "Here is the list of labels: " + LABEL
                location_label = self.__openai_service.ask_question(prompt + location_data_str + label, LocationLabelsExtract)
                if location_label:
                    tour_data.vi_location_attributes_label = location_label.vi_location_attributes_label
                    tour_data.en_location_attributes_label = location_label.en_location_attributes_label
            except Exception as e:
                print(f"Error converting user references to location labels: {e}")
                raise e
        else:
            tour_data.vi_location_attributes_label = data["vi_location_attributes_labels"]
            tour_data.en_location_attributes_label = data["en_location_attributes_labels"]
            
        if data["vi_food_attributes_labels"] == []:
            try:
                prompt = prompts.convert_user_food_references_to_labels_prompt
                food_data_str = "Here is the user's request list for food: " + ' '.join(str(user_references.food_attributes_to_str())) + '\n'
                label = "Here is the list of labels: " + LABEL
                food_label = self.__openai_service.ask_question(prompt + food_data_str + label, FoodLabelsExtract)
                if food_label:
                    tour_data.vi_food_attributes_label = food_label.vi_food_attributes_label
                    tour_data.en_food_attributes_label = food_label.en_food_attributes_label
            except Exception as e:
                print(f"Error converting user references to food labels: {e}")
                raise e
        else:
            tour_data.vi_food_attributes_label = data["vi_food_attributes_labels"]
            tour_data.en_food_attributes_label = data["en_food_attributes_labels"]

        return tour_data
        
    async def rerank_places_by_llm_async(self, places: list[PlaceWithScore], tour_ref: TourReferences):
        try:
            prompt = prompts.rerank_places_prompt
            data = "Here is the user's request information: " + str(tour_ref.attriutes_with_special_and_medical_conditions()) + '\n'
            label = "Here is the list of places: " + ''.join(str(place.to_dict_with_score()) for place in places)
            list_score = await self.__openai_service.ask_question_async(prompt + data + label, PlaceWithScoreCollapseList)
            for place in places:
                for score in list_score.places:
                    if place.id == score.id:
                        place.score = score.score
            return places
        except Exception as e:
            print(f"Error reranking places by LLM: {e}")
            raise e
        
    def generate_trip_items(self, breakfast_list: list[PlaceWithLocation], 
                            lunch_dinner_list: list[PlaceWithLocation], 
                            tourist_destination_list: list[PlaceWithLocation], 
                            day: int, locationsPerDay: int, locationPreference: float) -> list[dict]:
        # Generate trip items
        trip_items = []
        try:
            for i in range(day):
                # Add breakfast first
                current_trip = [breakfast_list.pop(0)]
                trip_items.append(TripItem(
                    trip_day=i + 1,
                    order_in_day=1,
                    place_id=current_trip[-1].id,
                    time_in_day=TimeInDay.MORNING.to_string(),
                ))

                # Determine morning and afternoon counts
                morning_count = (locationsPerDay - 3) // 2
                afternoon_count = (locationsPerDay - 3) // 2
                if (locationsPerDay - 3) % 2 != 0:
                    morning_count += 1  # Assign more to morning if odd

                morning_added = 0
                afternoon_added = 0

                for j in range(1, locationsPerDay):
                    if morning_added < morning_count:
                        # Add a morning destination
                        best_next_place = self.select_best_next_place(current_trip, tourist_destination_list, locationPreference)
                        current_trip.append(best_next_place)
                        trip_items.append(TripItem(
                            trip_day=i + 1,
                            order_in_day=j + 1,
                            place_id=best_next_place.id,
                            time_in_day=TimeInDay.MORNING.to_string(),
                        ))
                        tourist_destination_list.remove(best_next_place)
                        morning_added += 1
                    elif j == morning_count + 1:
                        # Add lunch
                        best_lunch_place = self.select_best_next_place(current_trip, lunch_dinner_list, locationPreference)
                        current_trip.append(best_lunch_place)
                        trip_items.append(TripItem(
                            trip_day=i + 1,
                            order_in_day=j + 1,
                            place_id=best_lunch_place.id,
                            time_in_day=TimeInDay.AFTERNOON.to_string(),
                        ))
                        lunch_dinner_list.remove(best_lunch_place)
                    elif afternoon_added < afternoon_count:
                        # Add an afternoon destination
                        best_next_place = self.select_best_next_place(current_trip, tourist_destination_list, locationPreference)
                        current_trip.append(best_next_place)
                        trip_items.append(TripItem(
                            trip_day=i + 1,
                            order_in_day=j + 1,
                            place_id=best_next_place.id,
                            time_in_day=TimeInDay.AFTERNOON.to_string(),
                        ))
                        tourist_destination_list.remove(best_next_place)
                        afternoon_added += 1
                    else:
                        # Add dinner
                        best_dinner_place = self.select_best_next_place(current_trip, lunch_dinner_list, locationPreference)
                        current_trip.append(best_dinner_place)
                        trip_items.append(TripItem(
                            trip_day=i + 1,
                            order_in_day=j + 1,
                            place_id=best_dinner_place.id,
                            time_in_day=TimeInDay.EVENING.to_string(),
                        ))
                        lunch_dinner_list.remove(best_dinner_place)
        except Exception as e:
            print(f"Error generating trip items: {e}")
            raise e

        return trip_items

    def select_best_next_place(self, current_trip: list[PlaceWithLocation], 
                               destination_list: list[PlaceWithLocation], 
                               locationPreference: float) -> PlaceWithLocation:
        # Select the best next place based on trip score
        candidate_trips = []
        for place in destination_list:
            if place not in current_trip:
                candidate_trip = current_trip + [place]
                candidate_trips.append(candidate_trip)

        best_trip_score = float('-inf')
        best_next_place = None
        for candidate_trip in candidate_trips:
            score = self.calculate_trip_score(candidate_trip, locationPreference)
            if score > best_trip_score:
                best_trip_score = score
                best_next_place = candidate_trip[-1]

        return best_next_place

    def calculate_trip_score(self, trip: list[PlaceWithLocation], locationPreference: float) -> float:
        # Calculate the score for a given trip based on location preference and other factors
        total_score = 0
        total_distance = 0

        total_score += sum(place.score for place in trip)
        for i in range(len(trip) - 1):
            data_distance = self.__distance_matrix_service.get_distance_time([trip[i].id, trip[i + 1].id])
            if data_distance is None:
                raise ValueError("Distance not found for trip calculation: "+ str(trip[i].id) + " to " + str(trip[i + 1].id))
            total_distance += data_distance[0]["distance"]* 1000  # Convert km to meters

        total_score = total_score - locationPreference * total_distance
        
        return total_score

    async def process_tour_data(self, breakfast_list, tourist_destination_list, lunch_dinner_list):
        tasks = [
            self.__distance_matrix_service.calculate_all_pairs(breakfast_list, tourist_destination_list),
            self.__distance_matrix_service.calculate_all_pairs(tourist_destination_list, tourist_destination_list),
            self.__distance_matrix_service.calculate_all_pairs(lunch_dinner_list, tourist_destination_list)
        ]
        await asyncio.gather(*tasks)

    def cache_labels(self, user_references: UserReferencesRequest):
        vi_location_attributes = []
        en_location_attributes = []
        vi_food_attributes = []
        en_food_attributes = []
        #search trip labels stored in database to cache location attributes labels
        location_cache = self.__trip_repository.search_trip_labels(
            user_references.location_attributes,[]) or None

        if location_cache:
            print("Location cache found")
            vi_location_attributes = extract_labels_from_string(location_cache["hits"]["hits"][0]["_source"]["trip_properties"]["vi_location_attributes_labels"]) or []
            en_location_attributes = extract_labels_from_string(location_cache["hits"]["hits"][0]["_source"]["trip_properties"]["en_location_attributes_labels"]) or []

        food_cache = self.__trip_repository.search_trip_labels(
            [],user_references.food_attributes) or None

        if food_cache:
            print("Food cache found")
            vi_food_attributes = extract_labels_from_string(food_cache["hits"]["hits"][0]["_source"]["trip_properties"]["vi_food_attributes_labels"]) or []
            en_food_attributes = extract_labels_from_string(food_cache["hits"]["hits"][0]["_source"]["trip_properties"]["en_food_attributes_labels"]) or []

        return {
            "vi_location_attributes_labels": vi_location_attributes,
            "en_location_attributes_labels": en_location_attributes,
            "vi_food_attributes_labels": vi_food_attributes,
            "en_food_attributes_labels": en_food_attributes
        }

def parse_places_from_es_hits(hits: list[dict]) -> list[PlaceWithScore]:
    places = []
    for hit in hits:
        source = hit["_source"]
        place = PlaceWithScore(
            id=source["id"],
            en_name=source["en_name"], 
            vi_name=source["vi_name"],
            en_address=source["en_address"],
            vi_address=source["vi_address"],
            lat=source["lat"],
            long=source["long"],
            en_type=source["en_type"],
            vi_type=source["vi_type"],
            en_properties=source["en_properties"],
            vi_properties=source["vi_properties"],
            images=source["images"],
            score=hit.get("_score")
        )
        places.append(place)
    return places

def pre_store_trip(trip_items: list, location_store_list: TripItemResearchList, breakfast_store_list: TripItemResearchList, lunch_dinner_store_list: TripItemResearchList) -> str:
    for item in trip_items:
        if location_store_list.set_is_selected(item.place_id):
            continue
        if breakfast_store_list.set_is_selected(item.place_id):
            continue
        if lunch_dinner_store_list.set_is_selected(item.place_id):
            continue