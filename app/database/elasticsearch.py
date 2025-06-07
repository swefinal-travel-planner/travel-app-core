import ssl
from elasticsearch import Elasticsearch
from injector import inject

class ElasticsearchClient:
    @inject
    def __init__(self, host, port, username, password):
        try:
            self.__es = Elasticsearch([{'host': host, 'port': port, 'scheme': 'http'}],
                                    basic_auth=(username, password),
                                    verify_certs=False)
            
            if self.__es.ping():
                print("Connected to Elasticsearch successfully.")
            else:
                print("Could not connect to Elasticsearch.")
                print(self.__es.info())
                raise Exception("Could not connect to Elasticsearch")
        except Exception as e:
            print(f"Error connecting to Elasticsearch: {e}")
            raise Exception(f"Could not connect to Elasticsearch: {e}")
        
    def ping(self):
        return self.__es.ping()
    
    def get_info(self):
        return self.__es.info()
    
    def check_index(self, index_name):
        return self.__es.indices.exists(index=index_name)
    
    def create_index(self, index_name, mapping):
        if self.check_index(index_name):
            raise Exception(f"Index '{index_name}' already exists")
        self.__es.indices.create(index=index_name, body=mapping)

    def delete_index(self, index_name):
        if not self.check_index(index_name):
            raise Exception(f"Index '{index_name}' does not exist")
        self.__es.indices.delete(index=index_name)

    def insert(self, index_name, body):
        if not self.check_index(index_name):
            raise Exception(f"Index '{index_name}' does not exist") 
        result = self.__es.index(index=index_name, body=body)
        if result['result'] != 'created':
            raise Exception(f"Failed to insert document into index '{index_name}'")
        return result['_id']
    
    def delete_by_query(self, index_name, body):
        if not self.check_index(index_name):
            raise Exception(f"Index '{index_name}' does not exist")
        result = self.__es.delete_by_query(index=index_name, body=body)
        if result['deleted'] == 0:
            raise Exception(f"No documents deleted in index '{index_name}'")
        return result
    
    def search_by_query(self, index_name, body):
        if not self.check_index(index_name):
            raise Exception(f"Index '{index_name}' does not exist")
        result = self.__es.search(index=index_name, body=body)
        if result['hits']['total']['value'] == 0:
            return None
        return result