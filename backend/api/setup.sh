# Run once
fission env create --spec --name python-api --image fission/python-env --builder fission/python-builder

# Toot API 
fission package create --spec --name toot --source ./toot/__init__.py --source ./toot/toot.py  --source ./toot/*.txt --source ./toot/*.sh --env python-api --buildcmd './build.sh'
fission function create --spec --name toot --env python-api --pkg toot --entrypoint "toot.main" --configmap shared-conf
fission route create --spec --name toot --function toot --method GET --url '/toot/{index}'

# Sudo API 
fission package create --spec --name sudo --source ./sudo/__init__.py --source ./sudo/sudo.py  --source ./sudo/*.txt --source ./sudo/*.sh --env python-api --buildcmd './build.sh'
fission function create --spec --name sudo --env python-api --pkg sudo --entrypoint "sudo.main" --configmap shared-conf
fission route create --spec --name sudo --function sudo --method GET --url '/sudo/{index}'

# Apply the specs
fission spec apply --specdir ./specs --wait
# fission spec apply --specdir fission/specs --watch
