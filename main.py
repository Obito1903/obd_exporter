import obd
from obd import OBDResponse, Async
import yaml
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

def connect_elm327() -> obd.Async:
    # TODO: Bluetooth connection
    # Connect to the OBD-II adapter
    return obd.Async("/dev/rfcomm0", delay_cmds=1)

def connect_influx() -> InfluxDBClient:
    token = cfg["influx"]["token"]
    org = cfg["influx"]["org"]
    url = cfg["influx"]["url"]

    return influxdb_client.InfluxDBClient(url=url, token=token, org=org)

obd_client = connect_elm327()
influx = connect_influx()

bucket = cfg["influx"]["bucket"]

write_api = influx.write_api()

def write_to_influx(r: OBDResponse):
    if r.value is None:
        return
    print(f"Writing to InfluxDB: {r.command.name} = {r.value} {cfg['PIDs'][r.command.name.lower()]['unit']}")
    point = Point(r.command.name).tag("unit", cfg["PIDs"][r.command.name.lower()]["unit"]).field("value", r.value.magnitude)
    # Log before writing to InfluxDB
    write_api.write(bucket=bucket, org="obicorp", record=point)

def enable_pids():
    for name, pid in cfg["PIDs"].items():
        if pid["enabled"]:
            print(f"Enabling PID: {name}")
            obd_client.watch(obd.commands[name.upper()], callback=write_to_influx, force=True)

enable_pids()

while True:
    obd_client.start()
