from injector import inject
from app.database.elasticsearch import ElasticsearchClient
from index_mapping.place_mapping import place_mapping
from app.models.place import Place

class PlaceRepository:
    @inject
    def __init__(self, db:ElasticsearchClient):
        self.db = db
        self.index_name = 'places'
        self.mapping = place_mapping

        if not self.db.check_index(self.index_name):
            try:
                self.db.create_index(self.index_name, self.mapping)
                print(f"Created index '{self.index_name}'")
            except Exception as e:
                print(f"Error creating index '{self.index_name}': {str(e)}")
        else:
            print(f"Index '{self.index_name}' already exists")

    def insert_place(self, place:Place, vector_embedding):
        mapper = {
            "name": place.name,
             "long": place.long,
            "lat": place.lat,
            "type": place.type,
            "properties": place.properties,
            "price": place.price,
            "place_vector": vector_embedding
        }

        
