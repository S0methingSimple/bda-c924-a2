from elasticsearch import Elasticsearch
import warnings
warnings.filterwarnings("ignore")

# connect to your elasticsearch address and port
es = Elasticsearch("https://localhost:9200", http_auth=('elastic', 'elastic'), verify_certs=False)

# check the index list
index_list = es.cat.indices(format="json")
print(index_list)
# MTYzMDU2ZTQzNGExZDU5

# source /Users/shen/Desktop/unimelb-comp90024-2024-grp-33-openrc.sh
# chmod 600 /Users/shen/Desktop/demokey.pem
# ssh -i /Users/shen/Desktop/demokey.pem -L 6443:$(openstack coe cluster show elastic -f json | jq -r '.master_addresses[]'):6443 ubuntu@$(openstack server show bastion -c addresses -f json | jq -r '.addresses["qh2-uom-internal"][]')
#
# kubectl port-forward service/elasticsearch-master -n elastic 9200:9200
#
# kubectl port-forward service/kibana-kibana -n elastic 5601:5601
