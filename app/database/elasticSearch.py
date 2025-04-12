import ssl
from elasticsearch import Elasticsearch

class ElasticsearchClient:
    def __init__(self, host='localhost', port=9200, api_key=None):
        ctx = ssl.create_default_context()
        ctx.load_verify_locations('./setup/ca.crt')
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT

        self.__es = Elasticsearch([{'host': host, 'port': port, 'scheme': 'https'}],
                                   api_key=api_key,
                                   verify_certs=True,
                                   ssl_context=ctx)
        
        if not self.ping():
            raise Exception("Could not connect to Elasticsearch")
        
    def ping(self):
        return self.__es.ping()

    def get_client(self):
        return self.__es