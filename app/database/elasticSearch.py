import ssl
from elasticsearch import Elasticsearch

class ElasticsearchClient:
    def __init__(self, host='localhost', port=9200, username='elastic', password=None):
        ctx = ssl.create_default_context()
        ctx.load_verify_locations('./setup/ca.crt')
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT

        self.__es = Elasticsearch([{'host': host, 'port': port, 'scheme': 'https'}],
                                   http_auth=(username, password),
                                   verify_certs=True,
                                   ssl_context=ctx)
        
        if not self.ping():
            raise Exception("Could not connect to Elasticsearch")
        
    def ping(self):
        try:
            return self.__es.ping()
        except Exception as e:
            print(f"Error pinging Elasticsearch: {e}")
            return e
    
    def check_index(self, index_name):
        try:
            return self.__es.indices.exists(index=index_name)
        except Exception as e:
            print(f"Error checking index '{index_name}': {e}")
            return e
    
    def create_index(self, index_name, mapping):
        try:
            if self.check_index(index_name):
                return Exception(f"Index '{index_name}' already exist")
            else:
                self.__es.indices.create(index=index_name, body=mapping)
                return True
        except Exception as e:
            print(f"Error creating index '{index_name}': {e}")
            return e  # Return the exception object on failure

    def insert_document(self, index_name, document):
        try:
            if not self.check_index(index_name):
                return Exception(f"Index '{index_name}' does not exist")
            else:
                result = self.__es.index(index=index_name, body=document)
                return result['_id']
        except Exception as e:
            print(f"Error inserting document into index '{index_name}': {e}")
            return e  # Return the exception object on failure

    def get_document_by_id(self, index_name, doc_id):

        if not self.check_index(index_name):
            return Exception(f"Index '{index_name}' does not exist")

        try:
            response = self.__es.get(index=index_name, id=doc_id)
            return response["_source"] if response["found"] else None
        except Exception as e:
            print(f"Error retrieving document with ID '{doc_id}' from index '{index_name}': {e}")
            return e  # Return the exception object on failure

    def delete_document(self, index_name, doc_id):
        if not self.check_index(index_name):
            return Exception(f"Index '{index_name}' does not exist")

        try:
            self.__es.delete(index=index_name, id=doc_id)
            return True  # Explicitly return True on success
        except Exception as e:
            print(f"Error deleting document with ID '{doc_id}' from index '{index_name}': {e}")
            return e  # Return the exception object on failure