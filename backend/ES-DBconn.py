from elasticsearch import Elasticsearch
import warnings
warnings.filterwarnings("ignore")

# connect to your elasticsearch address and port
es = Elasticsearch("https://localhost:9200", http_auth=('elastic', 'elastic'), verify_certs=False)

# check the index list
index_list = es.cat.indices(format="json")
print(index_list)
# MTYzMDU2ZTQzNGExZDU5