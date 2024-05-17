import json, time
from string import Template
from elasticsearch import Elasticsearch
from flask import request, current_app

# Expression to fetch toots from created_at date
toot_date_expr=Template('''{
                "range": {
                    "created_at": {
                        "gte": "${date}",
                        "lt": "${today}"
                    }
                }
            }''')       

# Expression to fetch all toots from index
toot_all_expr= '''{
    "match_all": {}
}'''

def config(k):
    with open(f'/configs/default/shared-conf/{k}', 'r') as f:
        return f.read()


def fetch_toots(es, idx, query):
    # Fetch toots from Elasticsearch
    try:
        response = es.search(index=idx, body=query)
    except Exception as e:
        current_app.logger.error(f'Error fetching toots: {e}')
        return None

    return response

def main():
    current_app.logger.info(f'Received request: ${request.headers}')

    # Get index and date from request headers
    try:
        idx= request.headers['X-Fission-Params-Index']
    except KeyError:
        current_app.logger.error('Missing Index parameter')
        return {
            "message": "Missing Index parameter"
        }

    current_app.logger.info(f'Sudo Index: {idx}')

    # Connect to Elasticsearch
    es = Elasticsearch(
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs= False,
        http_auth=(config('ES_USERNAME'), config('ES_PASSWORD'))
    )

    # Define query
    query = {
            "query": {
                "match_all": {}
            }
        }

    # Fetch toots
    response = fetch_toots(es, idx, query)

    if response:
        # Return response as json
        # current_app.logger.info(f'Response: {response}')
        current_app.logger.info('HELLO FROM SUDO')
        return {
            "status": 200,
            "message": "ok"
        }
    else:
        return  None