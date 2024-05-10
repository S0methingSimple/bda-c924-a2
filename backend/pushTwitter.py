import ijson
from elasticsearch import Elasticsearch, helpers
import warnings
warnings.filterwarnings("ignore")

# Connect to Elasticsearch
es = Elasticsearch("https://localhost:9200", http_auth=('elastic', 'elastic'), verify_certs=False)

# Path to the JSON file
file_path = "twitter-1gb.json"

# Index name
index_name = "twitter_data"

mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "created_at": {"type": "date"},
            "author_id": {"type": "keyword"},
            "sentiment": {"type": "float"},
            "text": {"type": "text"}
        }
    }
}

# Create the index if it doesn't exist
if not es.indices.exists(index=index_name):
    print("Index created successfully")
    es.indices.create(index=index_name, body=mapping)

# Function to generate batches from the JSON file
def generate_docs_in_batches(json_file, batch_size=1000):
    batch = []
    line_count = 0

    # Use `ijson` to read the JSON incrementally
    with open(json_file, 'r', encoding='utf-8') as file:
        # Use a path expression to navigate to the 'rows' field
        rows = ijson.items(file, 'rows.item')

        for record in rows:
            line_count += 1
            value_data = record['doc']['data']

            sentiment_data = value_data.get('sentiment', {})
            if isinstance(sentiment_data, dict) and len(sentiment_data) > 1:
                sentiment_score = 0.0
            else:
                sentiment_score = float(sentiment_data) if isinstance(sentiment_data, (int, float)) else 0.0

            batch.append({
                "_index": index_name,
                "_id": record['id'],
                "_source": {
                    "id": record['id'],
                    "created_at": value_data['created_at'],
                    "author_id": value_data['author_id'],
                    "sentiment": sentiment_score,
                    "text": value_data['text']
                }
            })

            # Yield a batch when the desired size is reached
            if len(batch) >= batch_size:
                print(f"Processed {line_count} lines")
                yield batch
                batch = []

    # Yield any remaining documents
    if batch:
        yield batch

# Perform bulk upload to Elasticsearch in batches
for batch in generate_docs_in_batches(file_path):
    helpers.bulk(es, batch)

print("Bulk upload completed.")
