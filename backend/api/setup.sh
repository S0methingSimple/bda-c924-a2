# Run once
fission env create --spec --name python-api --image fission/python-env --builder fission/python-builder
fission package create --spec --name toot --source ./function/__init__.py --source ./function/toot.py  --source ./function/*.txt --source ./function/*.sh --env python-api --buildcmd './build.sh'
fission function create --spec --name toot --env python-api --pkg toot --entrypoint "toot.main" --configmap shared-conf
fission route create --spec --name toot --function toot --method GET --url '/toot/{index}/{date:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}'

# Apply the specs
fission spec apply --specdir ./specs --wait
# fission spec apply --specdir fission/specs --watch

# curl -X GET "localhost:9200/housing_price/_search?pretty" -H 'Content-Type: application/json' -d'
# {
#     "query": {
#         "range": {
#             "created_at": {
#                 "gte": "2000-03-03",
#                 "lt": "2024-05-16"
#             }
#         }
#     }
# }
# '
