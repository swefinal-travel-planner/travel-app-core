from injector import inject
from app.database.elasticsearch import ElasticsearchClient
from index_mapping.place_mapping import place_mapping
from app.models.place import Place
from app.models.language import Language
from app.exceptions.custom_exceptions import ValidationError, NotFoundError, AppException

class PlaceRepository:
    @inject
    def __init__(self, db: ElasticsearchClient):
        self.__es = db
        self.__index_name = 'places'
        self.__mapping = place_mapping

        if not self.__es.check_index(self.__index_name):
            self.__es.create_index(self.__index_name, self.__mapping)
            print(f"Created index '{self.__index_name}'")
        else:
            print(f"Index '{self.__index_name}' already exists")

    def insert_place(self, place: Place, vector_embedding):
        mapper = {
            "id": place.id,
            "en_name": place.en_name,
            "vi_name": place.vi_name,
            "en_address": place.en_address,
            "vi_address": place.vi_address,
            "long": place.long,
            "lat": place.lat,
            "en_type": place.en_type,
            "vi_type": place.vi_type,
            "en_properties": place.en_properties,
            "vi_properties": place.vi_properties,
            "images": place.images,
            "place_vector": vector_embedding
        }
        if self.get_place_by_id(place.id):
            raise ValidationError(f"Document with ID '{place.id}' already exists")
        result = self.__es.insert(self.__index_name, mapper)
        print(f"Inserted document with ID '{place.id}'")
        return True

    def delete_place(self, place_id: str):
        if not self.get_place_by_id(place_id):
            raise NotFoundError(f"Document with ID '{place_id}' does not exist")
        query = {
            "query": {
                "term": {
                    "id": place_id
                }
            }
        }
        response = self.__es.delete_by_query(index=self.__index_name, body=query)
        print(f"Deleted document with ID '{place_id}'")
        return True

    def get_place_by_id(self, place_id: str):
        query = {
            "query": {
                "term": {
                    "id": place_id
                }
            }
        }
        response = self.__es.search_by_query(index_name=self.__index_name, body=query)
        if response is None:
            return None
        hits = response["hits"]["hits"]
        return hits[0]["_source"]
    
    def search_places_by_vector(self, vector_embedding, size):
        query = {
            "size": size,
            "knn": {  # Move 'knn' to the top level
                "field": "place_vector",  # Ensure the field name is correct
                "query_vector": vector_embedding,
                "k": size,
                "num_candidates": 1200,  # Number of candidates to consider
            },
            "_source": [  # Use '_source' to specify fields to retrieve
                "id", "en_name", "vi_name", "en_address", "vi_address", "long", "lat", 
                "en_type", "vi_type", "en_properties", "vi_properties", "images"
            ]
        }
        try:
            response = self.__es.search_by_query(index_name=self.__index_name, body=query)
            if response is None:
                return None
            hits = response["hits"]["hits"]
            return hits
        except Exception as e:
            raise AppException(f"Failed to perform vector search: {str(e)}")
        
    def search_places_after(self, limit: int, search_after_id: str, location: str, language: Language, filter: str = None, search_keyword: str = None):
        type_field = f"{language.to_string()}_type"
        properties_field = f"{language.to_string()}_properties"
        name_field = f"{language.to_string()}_name"
        print(f"Searching for places with location: {location}, filter: {filter}, language: {language}, limit: {limit}, search_after_id: {search_after_id}, search_keyword: {search_keyword}")
        query = {
            "size": limit,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                properties_field: location
                            }
                        }
                    ],
                    "filter": []
                }
            },
            "sort": [
                {"id": "asc"} 
            ],
            "_source": [
                "id", "long", "lat", "images"
            ]
        }
        # check language and add type field to query
        if language == Language.EN:
            query["_source"].extend(["en_name", "en_address", "en_type", "en_properties"])
        else:
            query["_source"].extend(["vi_name", "vi_address", "vi_type", "vi_properties"])

        # Add filter condition only if it is provided
        if filter is not None:
            query["query"]["bool"]["filter"].append({
                "match_phrase": {
                    type_field: filter
                }
            })

        if search_after_id is not None:
            query["search_after"] = [search_after_id]

        try:
            response = self.__es.search_by_query(index_name=self.__index_name, body=query)
            if response is None:
                return None
            hits = response["hits"]["hits"]
            # Correctly extract the "_source" field from each hit
            places = [hit["_source"] for hit in hits]
            if search_keyword:
                search_words = search_keyword.lower().split()
                def match_keyword(place):
                    name_value = place.get(name_field, "")
                    name = str(name_value).lower()
                    address_value = place.get(properties_field, "")
                    return all(word in name for word in search_words)
                places = [place for place in places if match_keyword(place)]
            return places
        except Exception as e:
            raise AppException(f"Failed to perform search after: {str(e)}")

    def get_places_in_patch_by_ids(self, language: Language, place_ids: list[str]):
        if not place_ids:
            return []

        query = {
            "query": {
                "terms": {
                    "id": place_ids
                }
            },
            "_source": [
                "id", "long", "lat", "images"
            ]
        }
        # check language to query
        if language == Language.EN:
            query["_source"].extend(["en_name", "en_address", "en_type", "en_properties"])
        else:
            query["_source"].extend(["vi_name", "vi_address", "vi_type", "vi_properties"])

        response = self.__es.search_by_query(index_name=self.__index_name, body=query)
        if response is None:
            return []
        hits = response["hits"]["hits"]
        return [hit["_source"] for hit in hits]

    def get_random_places(self, language: Language, limit: int):
        query = {
            "size": limit,
            "query": {
                "function_score": {
                    "query": {"match_all": {}},
                    "random_score": {}
                }
            },
            "_source": [
                "id", "long", "lat", "images"
            ]
        }
        # check language to query
        if language == Language.EN:
            query["_source"].extend(["en_name", "en_address", "en_type", "en_properties"])
        else:
            query["_source"].extend(["vi_name", "vi_address", "vi_type", "vi_properties"])

        response = self.__es.search_by_query(index_name=self.__index_name, body=query)
        if response is None:
            return []
        hits = response["hits"]["hits"]
        return [hit["_source"] for hit in hits]