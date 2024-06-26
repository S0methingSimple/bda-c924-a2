import json
import warnings
from elasticsearch import Elasticsearch
from flask import request, current_app


def config(k):
    with open(f'/configs/default/shared-conf/{k}', 'r') as f:
        return f.read()


def fetch_toots(idx, query, fetch_type):

    # Connect to Elasticsearch
    es = Elasticsearch(
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs=False,
        http_auth=(config('ES_USERNAME'), config('ES_PASSWORD'))
    )

    response = None
    try:
        if fetch_type == 'count':
            response = es.count(index=idx, body=query)
        else:
            response = es.search(index=idx, body=query, size=10000)
    except Exception as e:
        current_app.logger.error(f'Error fetching toots: {e}')

    return response


def main():

    # Ignore es warnings
    warnings.filterwarnings("ignore")

    # Get index and date from request headers
    try:
        idx = request.headers['X-Fission-Params-Index']
    except KeyError:
        current_app.logger.error('Missing Index parameter')
        return {
            "message": "Missing Index parameter"
        }

    # Get query params
    url_query = request.headers['X-Fission-Full-Url'].split('?')
    query_params = {}
    if len(url_query) > 1:
        query_params = dict(pair.split('=') for pair in url_query[1].split('&'))

    # Check type
    fetch_type = query_params.get('type', "count")

    # Define query
    if 'start_date' in query_params and 'end_date' in query_params:
        start_date, end_date = query_params['start_date'], query_params['end_date']
        query = {
            "query": {
                "range": {
                    "created_at": {
                        "gte": start_date,
                        "lt": end_date
                    }
                }
            }
        }
        current_app.logger.info(f'[FETCH] {fetch_type} Toot: {idx} | Date: {start_date} - {end_date}')
    else:
        query = {"query": {"match_all": {}}}
        current_app.logger.info(f'[FETCH] {fetch_type} Toot: {idx} | No Date Range ')


# Fetch toots
    response = fetch_toots(idx, query, fetch_type)

    if response:
        # Return response as json
        result = None
        try:
            if fetch_type == 'count':
                if "count" in response:
                    result = {
                        "count": response.get("count")
                    }
                else:
                    result = {
                        "count": 0
                    }
            else:
                hits = response.get("hits").get("hits")
                result = [toot["_source"] for toot in hits]
        except AttributeError:
            current_app.logger.error('No hits found')
            return None

        return json.dumps(result)
    else:
        return None
