from mastodon import Mastodon
from elasticsearch import Elasticsearch
from datetime import datetime, timezone

mastodon = Mastodon(api_base_url='https://mastodon.au')

es = Elasticsearch(
    hosts=["https://localhost:9200"],
    http_auth=('elastic', 'elastic'),
    verify_certs=False
)

index_tag_pairs = {
    "income": "income",
    "housing_price": "housing price",
    "property_price": "property price",
    "rental_price": "rental price",
    "rent": "rent",
    "studying": "studying",
    "visa": "visa",
    "mortgage": "mortgage",
    "migration": "migration",
    "immigration": "immigration"
}

mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "created_at": {"type": "date"},
            "content": {"type": "text"},
            "account": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "username": {"type": "text"}
                }
            },
            "tags": {"type": "keyword"}
        }
    }
}

for index_name in index_tag_pairs.keys():
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=mapping)

start_date = datetime(2011, 1, 1, tzinfo=timezone.utc)
end_date = datetime(2021, 1, 1, tzinfo=timezone.utc)

start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

def format_toot_for_es(toot):
    return {
        "id": toot["id"],
        "created_at": toot["created_at"],
        "content": toot["content"],
        "account": {
            "id": toot["account"]["id"],
            "username": toot["account"]["username"]
        },
        "tags": [tag["name"] for tag in toot["tags"]]
    }

def crawl_data_by_tag(index_name, tag):
    max_id = None
    while True:
        print(index_name, tag, max_id)
        toot_search_results = mastodon.timeline_hashtag(hashtag=tag,max_id=max_id,limit=40)

        if not toot_search_results:
            break

        for toot in toot_search_results:
            toot_id = toot["id"]

            created_at = toot['created_at']
            if created_at < start_date:
                continue

            formatted_toot = format_toot_for_es(toot)

            es.index(index=index_name, id=toot_id, body=formatted_toot)

        max_id = toot_search_results[-1]["id"]

for index_name, tag in index_tag_pairs.items():
    crawl_data_by_tag(index_name, tag)
