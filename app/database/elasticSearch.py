import ssl
from elasticsearch import Elasticsearch

class ElasticsearchClient:
    def __init__(self, host='localhost', port=9200, username='elastic', password=None):
        ctx = ssl.create_default_context()
        ctx.load_verify_locations('./setup/ca.crt')
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT

        self.es = Elasticsearch([{'host': host, 'port': port, 'scheme': 'https'}],
                                http_auth=(username, password),
                                verify_certs=True,
                                ssl_context=ctx)
        
        if not self.ping():
            raise Exception("Could not connect to Elasticsearch")
        
    def ping(self):
        return self.es.ping()
    
    def check_index(self, index_name):
        return self.es.indices.exists(index=index_name)
    
    def create_index(self, index_name, mapping):
        if self.es.indices.exists(index=index_name):
            raise Exception(f"Index '{index_name}' already exists")
        else:
            self.es.indices.create(index=index_name, body=mapping)

    def insert_document(self, index_name, document):
        if not self.check_index(index_name):
            raise Exception(f"Index '{index_name}' does not exist")
        
        self.es.index(index=index_name, body=document)