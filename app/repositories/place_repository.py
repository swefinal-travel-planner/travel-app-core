from injector import inject
from app.database.elasticsearch import ElasticsearchClient
from index_mapping.place_mapping import place_mapping 

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
