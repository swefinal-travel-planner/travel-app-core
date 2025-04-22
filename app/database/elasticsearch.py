import ssl
from elasticsearch import Elasticsearch

class ElasticsearchClient:
    def __init__(self, host='localhost', port=9200, username='elastic', password=None):
        try:
            self.__es = Elasticsearch([{'host': host, 'port': port, 'scheme': 'https'}],
                                    http_auth=(username, password),
                                    ssl_context=ssl.create_default_context(cafile="./setup/ca.crt"),
                                    verify_certs=True)
        except Exception as e:
            print(f"Error connecting to Elasticsearch: {e}")
            raise Exception(f"Could not connect to Elasticsearch: {e}")
        
    def ping(self):
        return self.__es.ping()

    def get_client(self):
        return self.__es
    
    def get_info(self):
        return self.__es.info()