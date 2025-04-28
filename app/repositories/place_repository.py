from injector import inject
from app.database.elasticsearch import ElasticsearchClient
from index_mapping.place_mapping import place_mapping
from app.models.place import Place
from app.exceptions.custom_exceptions import ValidationError, NotFoundError, AppException

class PlaceRepository:
    @inject
    def __init__(self, db: ElasticsearchClient):
        self.__es = db.get_client()
        self.__index_name = 'places'
        self.__mapping = place_mapping

        if not self.check_index(self.__index_name):
            self.create_index(self.__index_name, self.__mapping)
            print(f"Created index '{self.__index_name}'")
        else:
            print(f"Index '{self.__index_name}' already exists")

    def check_index(self, index_name):
        return self.__es.indices.exists(index=index_name)

    def create_index(self, index_name, mapping):
        if self.check_index(index_name):
            raise ValidationError(f"Index '{index_name}' already exists")
        self.__es.indices.create(index=index_name, body=mapping)

    def insert_place(self, place: Place, vector_embedding):
        mapper = {
            "id": place.id,
            "en_name": place.en_name,
            "vi_name": place.vi_name,
            "long": place.long,
            "lat": place.lat,
            "en_type": place.en_type,
            "vi_type": place.vi_type,
            "en_properties": place.en_properties,
            "vi_properties": place.vi_properties,
            "place_vector": vector_embedding
        }
        if not self.check_index(self.__index_name):
            raise NotFoundError(f"Index '{self.__index_name}' does not exist")
        if self.get_place_by_id(place.id):
            raise ValidationError(f"Document with ID '{place.id}' already exists")
        result = self.__es.index(index=self.__index_name, body=mapper)
        if result['result'] != 'created':
            raise AppException(f"Failed to insert document with ID '{place.id}'")
        print(f"Inserted document with ID '{place.id}'")
        return True

    def delete_place(self, place_id: int):
        if not self.check_index(self.__index_name):
            raise NotFoundError(f"Index '{self.__index_name}' does not exist")
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
        if response['deleted'] == 0:
            raise AppException(f"Failed to delete document with ID '{place_id}'")
        print(f"Deleted document with ID '{place_id}'")
        return True

    def get_place_by_id(self, place_id: int):
        if not self.check_index(self.__index_name):
            raise NotFoundError(f"Index '{self.__index_name}' does not exist")
        query = {
            "query": {
                "term": {
                    "id": place_id
                }
            }
        }
        response = self.__es.search(index=self.__index_name, body=query)
        hits = response["hits"]["hits"]
        return hits[0]["_source"] if hits else None
    
    def health_check_elastic(self):
        if not self.__es.ping():
            raise AppException("Elasticsearch is not healthy")
        return self.__es.info()