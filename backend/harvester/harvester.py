from mastodon import Mastodon
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta, timezone


def main():
    print("Start!")
    mastodon = Mastodon(api_base_url='https://mastodon.au')
    es = Elasticsearch(
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs=False,
        basic_auth=('elastic', 'elastic')
    )

    index_tag_pairs = {
        "income": "income",
        "housing_price": "housing price",
        "property_price": "property",
        "rental_price": "rental",
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
            print("Instance not found", index_name)
            es.indices.create(index=index_name, body=mapping)
        else:
            print("Instance found", index_name)

    current_time = datetime.now(timezone.utc)
    start_time = current_time - timedelta(days=2)

    empty_tags = []
    for index_name, tag in index_tag_pairs.items():
        max_id = None
        while True:
            toot_search_results = mastodon.timeline_hashtag(hashtag=tag, max_id=max_id, limit=1)
            if not toot_search_results:
                print("No info about: ", tag)
                empty_tags.append("NO" + tag)
                break

            found_valid_toot = False
            for toot in toot_search_results:
                created_at = toot['created_at']
                if created_at < start_time:
                    empty_tags.append(str(start_time) + tag + str(created_at))
                    # empty_tags.append(str(created_at))
                    # # empty_tags.append(str(toot["content"]))
                    # empty_tags.append(str(start_time))
                    break
                found_valid_toot = True
                formatted_toot = {
                    "id": toot["id"],
                    "created_at": toot["created_at"],
                    "content": toot["content"],
                    "account": {
                        "id": toot["account"]["id"],
                        "username": toot["account"]["username"]
                    },
                    "tags": [tag["name"] for tag in toot["tags"]]
                }
                es.index(index=index_name, id=toot["id"], body=formatted_toot)
                # empty_tags.append("!!!!!!!!!")
                # empty_tags.append(str(created_at))
                # empty_tags.append(str(toot["content"]))
                # empty_tags.append("!!!!!!!!!!!!!")
            if not found_valid_toot:
                break
            max_id = toot_search_results[-1]["id"]

    return " ".join(empty_tags)

# Japan_index_tag_pairs = {
#     "income": "所得",
#     "housing_price": "住宅価格",
#     "property_price": "不動産価格",
#     "rental_price": "レンタル価格",
#     "rent": "家賃",
#     "studying": "勉強する",
#     "visa": "ビザ",
#     "mortgage": "モーゲージ",
#     "migration": "移住",
#     "immigration": "移民"
# }
