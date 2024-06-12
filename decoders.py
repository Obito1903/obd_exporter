import obd
import obd.decoders
import math
import functools
from obd.utils import *
from obd.UnitsAndScaling import Unit, UAS_IDS

def power_from_maf(messages):
    obd.decoders.uas(0x27)(messages)
    maf = messages[0].value
    power = maf * 0.834
    return power

def audi_fuel_rate(messages):
    d = messages[0].data[3:]
    v = bytes_to_int(d)
    v = v * 0.05
    return v * Unit.liters_per_hour

def audi_temp(messages):
    d = messages[0].data[3:]
    v = bytes_to_int(d)
    v = v - 40
    return Unit.Quantity(v, Unit.celsius)



decoders = dict()

decoders["count"] = obd.decoders.count
decoders["rpm"] = obd.decoders.uas(0x07)
decoders["maf"] = obd.decoders.uas(0x27)
decoders["power_from_maf"] = power_from_maf
decoders["temp"] = obd.decoders.temp
decoders["fuel_rate"] = obd.decoders.fuel_rate

decoders["audi_fuel_rate"] = audi_fuel_rate
decoders["audi_temp"] = audi_temp
