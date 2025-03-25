import os
from elasticsearch import Elasticsearch

class ElasticsearchClient:
    def __init__(self, host='localhost', port=9200, username='elastic', password=None):
        self.es = Elasticsearch([{'host': host, 'port': port, 'scheme': 'https'}],
                                http_auth=(username, password),
                                verify_certs=True,
                                ca_certs='./setup/ca.crt')
        
        if not self.ping():
            raise Exception("Could not connect to Elasticsearch")
        
    def ping(self):
        print(self.es.info())
        return self.es.ping()
    
    def check_index(self, index_name):
        return self.es.indices.exists(index=index_name)
    
    def create_index(self, index_name, mapping):
        if self.es.indices.exists(index=index_name):
            raise Exception(f"Index '{index_name}' already exists")
        else:
            self.es.indices.create(index=index_name, body=mapping)