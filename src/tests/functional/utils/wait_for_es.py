from elasticsearch import Elasticsearch
import time


def wait_elastic():
    elastic = Elasticsearch(hosts=[f'es:9200'])
    ping = False
    while not ping:
        ping = elastic.ping()
        time.sleep(1)
    elastic.close()


if __name__ == '__main__':
    wait_elastic()
