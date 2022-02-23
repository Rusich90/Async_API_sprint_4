import backoff
from elasticsearch import Elasticsearch


@backoff.on_exception(backoff.expo,
                      ConnectionError)
def wait_elastic():
    elastic = Elasticsearch(hosts=[f'es:9200'])
    ping = elastic.ping()
    if not ping:
        raise ConnectionError()
    elastic.close()


if __name__ == '__main__':
    wait_elastic()
