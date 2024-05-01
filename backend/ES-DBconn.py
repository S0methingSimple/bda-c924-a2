from elasticsearch import Elasticsearch
import warnings
warnings.filterwarnings("ignore")

# connect to your elasticsearch address and port
es = Elasticsearch("http://localhost:9200")

# check the index list
index_list = es.cat.indices(format="json")
print(index_list)

# modify your index_settings
index_settings = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {
            "id": {
                "type": "keyword"
            },
            "location": {
                "type": "text"
            },
            "price": {
                "type": "short"
            },
            "year": {
                "type": "short"
            }
        }
    }
}

# create index
index_name = "property"
es.indices.create(index=index_name, body=index_settings)
index_list = es.cat.indices(format="json")
info = [index for index in index_list if index["index"] == "property"]
print(info)
# get mapping of index
mapping = es.indices.get_mapping(index=index_name)
print(mapping)

# delete index
es.indices.delete(index='example', ignore=[400, 404])
index_list = es.cat.indices(format="json")
info = [index for index in index_list if index["index"] == "property"]
print(info)

# determine the query rules
query = {"query": {"match_all": {}}}

result = es.search(index=index_name, body=query, size=10000)
print(result)

# determine the query rules
query = {"query": {"match_all": {}}}

result = es.search(index=index_name, body=query, size=10000)
print(result)

document_data = {
    "location": "MEL",
    "price": 1000,
    "year": 2019
}

# insert document using auto id
es.index(index=index_name, body=document_data)

# define your query
query = {
    "query": {
        "match": {
            "location": "MEL"
        }
    }
}

# execute the query
result = es.search(index=index_name, body=query)
for hit in result['hits']['hits']:
    print(hit['_source'])
