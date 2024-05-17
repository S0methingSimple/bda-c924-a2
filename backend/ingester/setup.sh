# Run once
fission specs init
fission env create --spec --name python-ingest --image fission/python-env --builder fission/python-builder

# Ingester Setup 
fission package create --spec --name ingester --source ./ingester/__init__.py --source ./ingester/ingester.py  --source ./ingester/*.txt --source ./ingester/*.sh --env python-ingest --buildcmd './build.sh'
fission function create --spec --name ingester --env python-ingest --pkg ingester --entrypoint "ingester.main" --configmap shared-conf
fission mqtrigger create --spec --name toot-ingest --spec --function ingester --mqtype kafka --mqtkind keda --topic toots --errortopic errors --maxretries 3 --metadata bootstrapServers=my-cluster-kafka-bootstrap.kafka.svc:9092 --metadata consumerGroup=my-group --cooldownperiod=30 --pollinginterval=5

# Apply the specs
fission spec apply --specdir ./specs --wait
# fission spec apply --specdir fission/specs --watchz
