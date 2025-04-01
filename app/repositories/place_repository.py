from injector import inject
from app.database.elasticsearch import ElasticsearchClient
from index_mapping.place_mapping import place_mapping
from app.models.place import Place

class PlaceRepository:
    @inject
    def __init__(self, db:ElasticsearchClient):
        self.__db = db
        self.__index_name = 'places'
        self.__mapping = place_mapping

        if not self.__db.check_index(self.__index_name):
            try:
                self.__db.create_index(self.__index_name, self.__mapping)
                print(f"Created index '{self.__index_name}'")
            except Exception as e:
                print(f"Error creating index '{self.__index_name}': {str(e)}")
                return e
        else:
            print(f"Index '{self.__index_name}' already exists")

    def insert_place(self, place: Place, vector_embedding):
        #check if the document exists
        # existing_doc = self.__db.get_document_by_id(self.__index_name, place.id)
        # if existing_doc:
        #     print(existing_doc)  # Log the existing document for debugging
        #     print(f"Document with ID '{place.id}' already exists. Skipping insertion.")
        #     return 1
        
        try:
            mapper = {
                "id": place.id,
                "name": place.name,
                "long": place.long,
                "lat": place.lat,
                "type": place.type,
                "properties": place.properties,
                "price": place.price,
                "place_vector": vector_embedding
            }
            self.__db.insert_document(self.__index_name, mapper)
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error inserting place: {e}")


    def delete_place(self, place_id: int):
        try:
            existing_doc = self.__db.get_document_by_id(self.__index_name, place_id)
            if existing_doc:
                self.__db.delete_document(self.__index_name, place_id)
                print(f"Deleted document with ID '{place_id}'")
            else:
                print(f"No document found with ID '{place_id}'. Cannot delete.")
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error deleting place with ID '{place_id}': {e}")