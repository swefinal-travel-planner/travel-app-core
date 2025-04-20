import ssl
from elasticsearch import Elasticsearch

class ElasticsearchClient:
    def __init__(self, host='localhost', port=9200, username='elastic', password=None):
        print("host: ", host)
        print("port: ", port)
        print("username: ", username)
        print("password: ", password)
        try:
            self.__es = Elasticsearch([{'host': host, 'port': port, 'scheme': 'http'}],
                                    http_auth=(username, password))
        except Exception as e:
            print(f"Error connecting to Elasticsearch: {e}")
            raise Exception(f"Could not connect to Elasticsearch: {e}")
        
    def ping(self):
        return self.__es.ping()

    def get_client(self):
        return self.__es
    
    def get_info(self):
        return self.__es.info()