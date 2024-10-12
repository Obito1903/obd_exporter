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
  --remote-api-token <token> \
  --remote-org-id <id>
```

```bash
influx replication create \
  --name car-copilot \
  --remote-id <id> \
  --local-bucket-id <id> \
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
