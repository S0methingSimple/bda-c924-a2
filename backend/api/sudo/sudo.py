import json, warnings
from elasticsearch import Elasticsearch
from flask import request, current_app

# Indices and their respective fields to be fetched
INDICES = {
    "median-house-price": { "index": "as4_median_housing_price2010_2014",  "source" : [" sa4_code", " sa4_name", " rpp_att_dwell_med_sal_prc_aud", "rpp_hse_med_sal_prc_aud", " year"]},
    "building-approvals": { "index": "building_approvals2011-2020", "source": [" sa4_code", " sa4_name", " value_new_oth_resial_building_aud000", " value_tot_building_aud000", "value_tot_resial_building_aud000", " value_new_houses_aud000", "yr"]},
    "economy-and-industry": { "index": "economy_and_industry_2014-2019", "source": [" sa4_code_2016", " sa4_name_2016", " rsdntl_prprty_prcs_yr_endd_30_jne_hss_mdn_sle_prce", " rsdntl_prprty_prcs_yr_endd_30_jne_attchd_dwllngs_mdn_sle_prce", " yr"]},
    "medians-and-averages": { "index": "selected_medians_and_averages_2011_2016_2021", "source": [" SA4_MAIN11", " SA4_NAME11", " Median_rent_weekly", "yr"]},
}

def config(k):
    with open(f'/configs/default/shared-conf/{k}', 'r') as f:
        return f.read()


def fetch_data(index, query):

    # Connect to Elasticsearch
    es = Elasticsearch(
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs= False,
        http_auth=(config('ES_USERNAME'), config('ES_PASSWORD'))
    )

    response = None
    try:
        response = es.search(index=index, body=query, size=10000)
    except Exception as e:
        current_app.logger.error(f'Error fetching data: {e}')

    return response

def main():

    # Ignore es warnings
    warnings.filterwarnings("ignore")

    # Get index and date from request headers
    try:
        index_source = INDICES[request.headers['X-Fission-Params-Index']]
        current_app.logger.info(f'[FETCH] SUDO Index: {index_source["index"]}')
    except KeyError:
        current_app.logger.error('Missing or Incorrect Index parameter')
        return {
            "message": "Missing or Incorrect Index parameter"
        }

    # Define query
    query = {
            "query": {
                "match_all": {}
            },
            "_source": index_source["source"]
         }

    # Fetch from ES
    response = fetch_data(index_source["index"], query)

    if response:
        # Return response as json
        source_hits = []
        try :
            hits = response.get("hits").get("hits")
            source_hits = [item["_source"] for item in hits]
        except AttributeError:
            current_app.logger.error('No hits found')
            return None

        return json.dumps(source_hits)
    else:
        return  None