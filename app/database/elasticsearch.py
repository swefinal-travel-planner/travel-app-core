import ssl
from elasticsearch import Elasticsearch

class ElasticsearchClient:
    def __init__(self, host='localhost', port=9200, username='elastic', password=None):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations('./setup/ca.crt')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_REQUIRED
        print("host: ", host)
        print("port: ", port)
        print("username: ", username)
        print("password: ", password)
        try:
            self.__es = Elasticsearch([{'host': host, 'port': port, 'scheme': 'https'}],
                                    http_auth=(username, password),
                                    verify_certs=True,
                                    ssl_context=ctx)
        except Exception as e:
            print(f"Error connecting to Elasticsearch: {e}")
            raise Exception(f"Could not connect to Elasticsearch: {e}")
        
    def ping(self):
        return self.__es.ping()

    def get_client(self):
        return self.__es