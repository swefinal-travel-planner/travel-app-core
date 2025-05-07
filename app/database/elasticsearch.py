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

    def get_client(self):
        return self.__es
    
    def get_info(self):
        return self.__es.info()