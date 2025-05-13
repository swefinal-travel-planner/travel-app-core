from injector import inject
from app.models.user_references_request import UserReferencesRequest
from app.models.tour_references import TourReferences
from app.models.place_with_score import PlaceWithScore
from app.models.place_with_score_collapse import PlaceWithScoreCollapse,PlaceWithScoreCollapseList
from app.models.place_with_location import PlaceWithLocation
from app.models.trip_item import TripItem, TripItemWithPlace
from app.models.time_in_day import TimeInDay
from app.models.location_preference import LocationPreference
from app.repositories.place_repository import PlaceRepository
from app.services.openai_service import OpenAIService
from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
from app.services.distance_matrix_service import DistanceMatrixService
import constant.prompt as prompts
from constant.label import LABEL
import asyncio

class TourService:
    @inject
    def __init__(self,
                place_repository: PlaceRepository, 
                embedding_service: EmbeddingService,
                openai_service: OpenAIService,
                distance_matrix_service: DistanceMatrixService):
        self.__openai_service = openai_service
        self.__place_repository = place_repository
        self.__embedding_service = embedding_service
        self.__distance_matrix_service = distance_matrix_service

    def create_tour(self, user_references: UserReferencesRequest):
        try:
            #convert user references to tour references in label
            tour_references = self.convert_user_references_to_tour_references(user_references)
            print("convert complete")

            #embedding location_attribute_label and food_attribute_label to vector
            location_attributes_label_embedding = self.__embedding_service.embed_text(str(tour_references.en_location_attributes_label) + "," + str(tour_references.vi_location_attributes_label))
            food_attributes_label_embedding = self.__embedding_service.embed_text(str(tour_references.en_food_attributes_label) + "," + str(tour_references.vi_food_attributes_label))
            print("embedding complete")

            #search for places in the database
            locations_places_list = self.__place_repository.search_places_by_vector(location_attributes_label_embedding, tour_references.days * (tour_references.locationsPerDay - 3) * 3)
            food_places_list = self.__place_repository.search_places_by_vector(food_attributes_label_embedding, tour_references.days * 3 * 3)
            print("search complete")

            #parse places from es hits and remove duplicates
            tourist_destination_list_parse = self.parse_places_from_es_hits(locations_places_list)
            food_location_list_parse = self.parse_places_from_es_hits(food_places_list)

            # Remove places from food_location_listaces that exist in locations_places_list (by id)
            food_place_ids = [hit.id for hit in food_location_list_parse]
            tourist_destination_list_parse = [
                place for place in tourist_destination_list_parse if place.id not in food_place_ids
            ]
            print("parse complete")

            #rerank places by
            #locations_rerank = self.rerank_places(locations_places, str(tour_references.en_location_attributes_label) + "," + str(tour_references.vi_location_attributes_label))
            #food_rerank = self.rerank_places(food_places, str(tour_references.en_food_attributes_label) + "," + str(tour_references.vi_food_attributes_label))

            #rerank places by llm
            rerank_list = self.rerank_places_by_llm(tourist_destination_list_parse + food_location_list_parse, tour_references)
            print("rerank by llm complete")

            #split places into tourist destination, breakfast, lunch, dinner
            tourist_destination_list = []
            breakfast_list = []
            lunch_dinner_list = []
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
                        else:
                            lunch_dinner_list.append(PlaceWithLocation(
                                id=place.id,
                                score=place.score,
                                lat=place.lat,
                                long=place.long,
                            ))
                    else:
                        tourist_destination_list.append(PlaceWithLocation(
                                id=place.id,
                                score=place.score,
                                lat=place.lat,
                                long=place.long,
                            ))
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
            #store trip items to database
            store_id = "abc"

            return {"reference_id": store_id, "trip_items" :[trip_item.to_dict() for trip_item in finalTripItems]}
        except Exception as e:
            print(f"Error creating tour: {e}")
            raise e
        
    def convert_user_references_to_tour_references(self, user_references: UserReferencesRequest) -> TourReferences:
        try:
            prompt = prompts.convert_user_references_to_tour_references_prompt
            data = "Đây là danh sách yêu cầu của người dùng: " + ''.join(str(user_references.to_dict())) + '\n'
            label = "Đây là danh sách các nhãn dán: " + LABEL
            return self.__openai_service.ask_question(prompt + data + label, TourReferences)
        except Exception as e:
            print(f"Error converting user references to tour references: {e}")
            raise e
    
    def parse_places_from_es_hits(self, hits: list[dict]) -> list[PlaceWithScore]:
        places = []
        for hit in hits:
            source = hit["_source"]
            place = PlaceWithScore(
                id=source["id"],
                en_name=source["en_name"],
                vi_name=source["vi_name"],
                lat=source["lat"],
                long=source["long"],
                en_type=source["en_type"],
                vi_type=source["vi_type"],
                en_properties=source["en_properties"],
                vi_properties=source["vi_properties"],
                score=hit.get("_score")
            )
            places.append(place)
        return places
    
    def rerank_places(self, places: list[PlaceWithScore], target_labels: str) -> list[PlaceWithScore]:

        rerank_places = self.__reranker_service.rerank(target_labels, [place.to_dict() for place in places])
        print(rerank_places)
        return rerank_places

    def rerank_places_by_llm(self, places: list[PlaceWithScore], tour_ref: TourReferences):
        try:
            prompt = prompts.rerank_places_prompt
            data = " Đây là thông tin về yêu cầu của người dùng: " + str(tour_ref.attriutes_with_special_and_medical_conditions()) + '\n'
            label = "Đây là danh sách các địa điểm: " + ''.join(str(place.to_dict_with_score()) for place in places)
            list_score = self.__openai_service.ask_question(prompt + data + label, PlaceWithScoreCollapseList)
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
            distance = self.__distance_matrix_service.find_distance(trip[i].id, trip[i + 1].id)
            if distance is None:
                raise ValueError("Distance not found for trip calculation: "+ str(trip[i].id) + " to " + str(trip[i + 1].id))
            total_distance += distance

        total_score = total_score - locationPreference * total_distance
        
        return total_score

    async def process_tour_data(self, breakfast_list, tourist_destination_list, lunch_dinner_list):
        # Ensure this function is asynchronous to await the calculate_all_pairs method
        await self.__distance_matrix_service.calculate_all_pairs(breakfast_list, tourist_destination_list)
        await self.__distance_matrix_service.calculate_all_pairs(tourist_destination_list, tourist_destination_list)
        await self.__distance_matrix_service.calculate_all_pairs(lunch_dinner_list, tourist_destination_list)