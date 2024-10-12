# car-exporter

## Setup

### Setup Influxdb on the edge

```bash
curl -LO https://download.influxdata.com/influxdb/releases/influxdb2_2.7.6-1_arm64.deb
sudo dpkg -i influxdb2_2.7.6-1_arm64.deb
sudo systemctl enable --now influxdb
```

```bash
influx setup \
  --username car-copilot \
  --password very-strongpassword \
  --org car-copilot \
  --bucket local \
  --force
```

Create a remote

```bash
influx remote create \
  --name car-copilot \
  --remote-url https://car-influx.obito.fr \
  --remote-api-token u51rc2Uqx-bEvuoDmojwIffQodQBumzIDA1-xZ841hUqhngdbFsHn7_pte3AfaxiJfhMb8nyXdMAU632twbPUA== \
  --remote-org-id 42f4d1e21ed1ed18
```

```bash
influx replication create \
  --name car-copilot \
  --remote-id 0d2f586d4d67d000 \
  --local-bucket-id 2a2d616cb27794b1 \
  --remote-bucket samuel
```

Create a token for local

```bash
influx auth create --all-access --org car-copilot
```

write token in config.yaml


### Setup python

Create a virtualenv

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
