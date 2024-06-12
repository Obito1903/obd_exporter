import obd
from obd import OBDResponse, Async,OBDCommand
import obd.decoders
import yaml
import binascii
from typing import List
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from decoders import decoders
import psycopg2
import socket

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

local = True

bucket = cfg["influx"]["bucket"]

write_api = influx.write_api()

current_car = cfg["car"]["brand"]+"_"+cfg["car"]["model"]+"_"+cfg["car"]["year"]+"_"+cfg["car"]["engine"]
current_car = current_car.lower()


# Merge profiles
if current_car in cfg["profiles"]:
    cfg["profiles"]["default"].update(cfg["profiles"][current_car])

profile = cfg["profiles"]["default"]

def register_trip(start: float, end: float):
    # Connect to postgresql
    print("Registering trip")
    conn =  psycopg2.connect(
        host=cfg['postgres']['host'],
        port=cfg['postgres']['port'],
        database=cfg['postgres']['db'],
        user=cfg['postgres']['user'],
        password=cfg['postgres']['mdp']
    )
    cur = conn.cursor()

    # Get owner id
    cur.execute(f"SELECT owner_id FROM owners WHERE name = '{cfg['owner']}'")
    owner_id = cur.fetchone()[0]
    print(owner_id)
    # Get car id
    cur.execute(f"SELECT car_id FROM car WHERE brand = '{cfg['car']['brand']}' AND model = '{cfg['car']['model']}' AND year = '{cfg['car']['year']}' AND engine = '{cfg['car']['engine']}'")
    car_id = cur.fetchone()[0]
    print(car_id)
    # Insert trip
    cur.execute(f"INSERT INTO trips (start, end, owner_id, car_id) VALUES ({start}, {end}, {owner_id}, {car_id})")
    conn.commit()

    cur.close()
    conn.close()
    print("Trip registered")

def check_power() -> bool:
    # Open TCP socket to check if power is on
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1",8423))
    client.send(b"get battery_power_plugged")
    response = client.recv(1024)
    client.close()
    print(response)
    if response == b"battery_power_plugged: true\n":
        return True
    else:
        return False

def ping_db() -> bool:
    # Check if pgsql is reachable
    response = os.system("ping -c 1 " + cfg["ping_host"])
    # and then check the response...
    if response == 0:
        pingstatus = True
    else:
        pingstatus = False

    return pingstatus

start = time.time()

def write(r: OBDResponse):
    if r.value is None:
        return
    # Check if engine running by checking if battery is charging
    if r.command.name == "SPEED" and not check_power():
        # stop obd client
        obd_client.close()

        end = time.time()

        # wait for internet connectivity
        while not ping_db:
            time.sleep(5)

        register_trip(start, end)

    if local:
        name = r.command.name.lower()

        if "name" in profile[r.command.name.lower()]:
            name = profile[r.command.name.lower()]["name"]

        print(f"{name} = {r.value} {profile[r.command.name.lower()]['unit']}")
    else:
        write_to_influx(r)

def write_to_influx(r: OBDResponse):
    if r.value is None:
        return

    name = r.command.name.lower()

    if "name" in profile[r.command.name.lower()]:
        name = profile[r.command.name.lower()]["name"]

    print(f"Writing to InfluxDB: {r.command.name} = {r.value} {profile[r.command.name.lower()]['unit']}")
    point = Point(name).tag("unit", profile[r.command.name.lower()]["unit"]).field("value", r.value.magnitude)
    # Log before writing to InfluxDB
    write_api.write(bucket=bucket, org=cfg["influx"]["org"], record=point)

def enable_pids():
    for name, pid in profile.items():
        command = OBDCommand
        if pid["enabled"]:
            if "pid" in pid.keys():
                description = pid["description"]
                # service = int(pid["service"]).to_bytes()
                custom_pid = str(pid["pid"]).encode()
                size = pid["size"]
                decoder_name = pid["decoder"]

                command = OBDCommand(name=name,desc=description, command=custom_pid,_bytes=size, decoder=decoders[decoder_name], header=b'7E0',)
                print(f"Enabling custom PID: {name} with PID {custom_pid}")
            else:
                command = obd.commands[name.upper()]
            # print(f"Enabling PID: {name}")
            obd_client.watch(command, callback=write, force=True)

enable_pids()

while True:
    obd_client.start()
