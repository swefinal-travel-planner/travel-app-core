import json
from injector import inject
from app.database.elasticsearch import ElasticsearchClient
from index_mapping.trip_mapping import trip_mapping
from app.models.tour_references import TourReferences
from app.models.trip_item_research import TripItemResearch, TripItemResearchList
from app.exceptions.custom_exceptions import ValidationError, NotFoundError, AppException
from utils.normalize_label_array import normalize_label_array

class TripRepository:
    @inject
    def __init__(self, db: ElasticsearchClient):
        self.__es = db
        self.__index_name = 'trips'
        self.__mapping = trip_mapping

        if not self.__es.check_index(self.__index_name):
            self.__es.create_index(self.__index_name, self.__mapping)
            print(f"Created index '{self.__index_name}'")
        else:
            print(f"Index '{self.__index_name}' already exists")

    def insert_trip(self, tour_reference: TourReferences, breakfast_list: TripItemResearchList, lunch_dinner_list: TripItemResearchList, location_list: TripItemResearchList):
        mapper = {
            "user_properties": {
                "location_attributes": normalize_label_array(tour_reference.location_attributes),
                "food_attributes": normalize_label_array(tour_reference.food_attributes),
            },
            "trip_properties": {
                "en_location_attributes_labels": normalize_label_array(tour_reference.en_location_attributes_label),
                "en_food_attributes_labels": normalize_label_array(tour_reference.en_food_attributes_label),
                "vi_location_attributes_labels": normalize_label_array(tour_reference.vi_location_attributes_label),
                "vi_food_attributes_labels": normalize_label_array(tour_reference.vi_food_attributes_label),
            },
            "trip_items": {
                "breakfast_list": breakfast_list.to_dict(),
                "lunch_dinner_list": lunch_dinner_list.to_dict(),
                "location_list": location_list.to_dict()
            }
        }
        result = self.__es.insert(self.__index_name, mapper)
        print(f"Inserted document complete with ID '{result}'")
        return result
    
    def search_trip_labels(self, location_attributes: list[str], food_attributes: list[str]):
        if not location_attributes and not food_attributes:
            raise ValidationError("At least one attribute must be provided")

        nested_must = []
        if location_attributes:
                nested_must.append({
                    "term": {
                        "user_properties.location_attributes": normalize_label_array(location_attributes)
                    }
                })
        if food_attributes:
                nested_must.append({
                    "term": {
                        "user_properties.food_attributes": normalize_label_array(food_attributes)
                    }
                })

        must_clauses = []
        if nested_must:
            must_clauses.append({
                "nested": {
                    "path": "user_properties",
                    "query": {
                        "bool": {
                            "must": nested_must
                        }
                    }
                }
            })

        query = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            },
            "_source": [
                "trip_properties.vi_location_attributes_labels",
                "trip_properties.vi_food_attributes_labels",
                "trip_properties.en_location_attributes_labels",
                "trip_properties.en_food_attributes_labels",
            ]
        }

        results = self.__es.search_by_query(self.__index_name, query)
        if not results:
            return []

        return results
