import obd
import obd.decoders


def power_from_maf(messages):
    obd.decoders.uas(0x27)(messages)
    maf = messages[0].value
    power = maf * 0.834
    return power

decoders = dict()

decoders["count"] = obd.decoders.count
decoders["rpm"] = obd.decoders.uas(0x07)
decoders["maf"] = obd.decoders.uas(0x27)
decoders["power_from_maf"] = power_from_maf
