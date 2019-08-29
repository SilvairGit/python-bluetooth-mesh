from math import pow, log
from construct import (
    Int8ul, Int16ul, Int24ul, Struct,
    Switch, this, Adapter, Probe, Flag, Array, Byte
)
from enum import IntEnum


class PropertyID(IntEnum):
    AVERAGE_AMBIENT_TEMPERATURE_IN_A_PERIOD_OF_DAY = 0x0001
    AVERAGE_INPUT_CURRENT = 0x0002
    AVERAGE_INPUT_VOLTAGE = 0x0003
    AVERAGE_OUTPUT_CURRENT = 0x0004
    AVERAGE_OUTPUT_VOLTAGE = 0x0005
    CENTER_BEAM_INTENSITY_AT_FULL_POWER = 0x0006
    CHROMATICITY_TOLERANCE = 0x0007
    COLOR_RENDERING_INDEX_R9 = 0x0008
    COLOR_RENDERING_INDEX_RA = 0x0009
    DEVICE_APPEARANCE = 0x000A
    DEVICE_COUNTRY_OF_ORIGIN = 0x000B
    DEVICE_DATE_OF_MANUFACTURE = 0x000C
    DEVICE_ENERGY_USE_SINCE_TURN_ON = 0x000D
    DEVICE_FIRMWARE_REVISION = 0x000E
    DEVICE_GLOBAL_TRADE_ITEM_NUMBER = 0x000F
    DEVICE_HARDWARE_REVISION = 0x0010
    DEVICE_MANUFACTURER_NAME = 0x0011
    DEVICE_MODEL_NUMBER = 0x0012
    DEVICE_OPERATING_TEMPERATURE_RANGE_SPECIFICATION = 0x0013
    DEVICE_OPERATING_TEMPERATURE_STATISTICAL_VALUES = 0x0014
    DEVICE_OVER_TEMPERATURE_EVENT_STATISTICS = 0x0015
    DEVICE_POWER_RANGE_SPECIFICATION = 0x0016
    DEVICE_RUNTIME_SINCE_TURN_ON = 0x0017
    DEVICE_RUNTIME_WARRANTY = 0x0018
    DEVICE_SERIAL_NUMBER = 0x0019
    DEVICE_SOFTWARE_REVISION = 0x001A
    DEVICE_UNDER_TEMPERATURE_EVENT_STATISTICS = 0x001B
    INDOOR_AMBIENT_TEMPERATURE_STATISTICAL_VALUES = 0x001C
    INITIAL_CIE_1931_CHROMATICITY_COORDINATES = 0x001D
    INITIAL_CORRELATED_COLOR_TEMPERATURE = 0x001E
    INITIAL_LUMINOUS_FLUX = 0x001F
    INITIAL_PLANCKIAN_DISTANCE = 0x0020
    INPUT_CURRENT_RANGE_SPECIFICATION = 0x0021
    INPUT_CURRENT_STATISTICS = 0x0022
    INPUT_OVER_CURRENT_EVENT_STATISTICS = 0x0023
    INPUT_OVER_RIPPLE_VOLTAGE_EVENT_STATISTICS = 0x0024
    INPUT_OVER_VOLTAGE_EVENT_STATISTICS = 0x0025
    INPUT_UNDER_CURRENT_EVENT_STATISTICS = 0x0026
    INPUT_UNDER_VOLTAGE_EVENT_STATISTICS = 0x0027
    INPUT_VOLTAGE_RANGE_SPECIFICATION = 0x0028
    INPUT_VOLTAGE_RIPPLE_SPECIFICATION = 0x0029
    INPUT_VOLTAGE_STATISTICS = 0x002A
    LIGHT_CONTROL_AMBIENT_LUXLEVEL_ON = 0x002B
    LIGHT_CONTROL_AMBIENT_LUXLEVEL_PROLONG = 0x002C
    LIGHT_CONTROL_AMBIENT_LUXLEVEL_STANDBY = 0x002D
    LIGHT_CONTROL_LIGHTNESS_ON = 0x002E
    LIGHT_CONTROL_LIGHTNESS_PROLONG = 0x002F
    LIGHT_CONTROL_LIGHTNESS_STANDBY = 0x0030
    LIGHT_CONTROL_REGULATOR_ACCURACY = 0x0031
    LIGHT_CONTROL_REGULATOR_KID = 0x0032
    LIGHT_CONTROL_REGULATOR_KIU = 0x0033
    LIGHT_CONTROL_REGULATOR_KPD = 0x0034
    LIGHT_CONTROL_REGULATOR_KPU = 0x0035
    LIGHT_CONTROL_TIME_FADE = 0x0036
    LIGHT_CONTROL_TIME_FADE_ON = 0x0037
    LIGHT_CONTROL_TIME_FADE_STANDBY_AUTO = 0x0038
    LIGHT_CONTROL_TIME_FADE_STANDBY_MANUAL = 0x0039
    LIGHT_CONTROL_TIME_OCCUPANCY_DELAY = 0x003A
    LIGHT_CONTROL_TIME_PROLONG = 0x003B
    LIGHT_CONTROL_TIME_RUN_ON = 0x003C
    LUMEN_MAINTENANCE_FACTOR = 0x003D
    LUMINOUS_EFFICACY = 0x003E
    LUMINOUS_ENERGY_SINCE_TURN_ON = 0x003F
    LUMINOUS_EXPOSURE = 0x0040
    LUMINOUS_FLUX_RANGE = 0x0041
    MOTION_SENSED = 0x0042
    MOTION_THRESHOLD = 0x0043
    OPEN_CIRCUIT_EVENT_STATISTICS = 0x0044
    OUTDOOR_STATISTICAL_VALUES = 0x0045
    OUTPUT_CURRENT_RANGE = 0x0046
    OUTPUT_CURRENT_STATISTICS = 0x0047
    OUTPUT_RIPPLE_VOLTAGE_SPECIFICATION = 0x0048
    OUTPUT_VOLTAGE_RANGE = 0x0049
    OUTPUT_VOLTAGE_STATISTICS = 0x004A
    OVER_OUTPUT_RIPPLE_VOLTAGE_EVENT_STATISTICS = 0x004B
    PEOPLE_COUNT = 0x004C
    PRESENCE_DETECTED = 0x004D
    PRESENT_AMBIENT_LIGHT_LEVEL = 0x004E
    PRESENT_AMBIENT_TEMPERATURE = 0x004F
    PRESENT_CIE_1931_CHROMATICITY_COORDINATES = 0x0050
    PRESENT_CORRELATED_COLOR_TEMPERATURE = 0x0051
    PRESENT_DEVICE_INPUT_POWER = 0x0052
    PRESENT_DEVICE_OPERATING_EFFICIENCY = 0x0053
    PRESENT_DEVICE_OPERATING_TEMPERATURE = 0x0054
    PRESENT_ILLUMINANCE = 0x0055
    PRESENT_INDOOR_AMBIENT_TEMPERATURE = 0x0056
    PRESENT_INPUT_CURRENT = 0x0057
    PRESENT_INPUT_RIPPLE_VOLTAGE = 0x0058
    PRESENT_INPUT_VOLTAGE = 0x0059
    PRESENT_LUMINOUS_FLUX = 0x005A
    PRESENT_OUTDOOR_AMBIENT_TEMPERATURE = 0x005B
    PRESENT_OUTPUT_CURRENT = 0x005C
    PRESENT_OUTPUT_VOLTAGE = 0x005D
    PRESENT_PLANCKIAN_DISTANCE = 0x005E
    PRESENT_RELATIVE_OUTPUT_RIPPLE_VOLTAGE = 0x005F
    RELATIVE_DEVICE_ENERGY_USE_IN_A_PERIOD_OF_DAY = 0x0060
    RELATIVE_DEVICE_RUNTIME_IN_A_GENERIC_LEVEL_RANGE = 0x0061
    RELATIVE_EXPOSURE_TIME_IN_AN_ILLUMINANCE_RANGE = 0x0062
    RELATIVE_RUNTIME_IN_A_CORRELATED_COLOR_TEMPERATURE_RANGE = 0x0063
    RELATIVE_RUNTIME_IN_A_DEVICE_OPERATING_TEMPERATURE_RANGE = 0x0064
    RELATIVE_RUNTIME_IN_AN_INPUT_CURRENT_RANGE = 0x0065
    RELATIVE_RUNTIME_IN_AN_INPUT_VOLTAGE_RANGE = 0x0066
    SHORT_CIRCUIT_EVENT_STATISTICS = 0x0067
    TIME_SINCE_MOTION_SENSED = 0x0068
    TIME_SINCE_PRESENCE_DETECTED = 0x0069
    TOTAL_DEVICE_ENERGY_USE = 0x006A
    TOTAL_DEVICE_OFF_ON_CYCLES = 0x006B
    TOTAL_DEVICE_POWER_ON_CYCLES = 0x006C
    TOTAL_DEVICE_POWER_ON_TIME = 0x006D
    TOTAL_DEVICE_RUNTIME = 0x006E
    TOTAL_LIGHT_EXPOSURE_TIME = 0x006F
    TOTAL_LUMINOUS_ENERGY = 0x0070


class ElectricCurrentValidator(Adapter):
    def _decode(self, obj, content, path):
        return obj/100

    def _encode(self, obj, content, path):
        return int(obj*100)


class VoltageValidator(Adapter):
    def _decode(self, obj, content, path):
        return None if obj == 0xffff else obj/64

    def _encode(self, obj, content, path):
        return 0xffff if obj is None else int(obj*64)


class Percentage8Validator(Adapter):
    def _decode(self, obj, content, path):
        return None if obj == 0xff else obj/2

    def _encode(self, obj, content, path):
        return 0xff if obj is None else int(obj*2)


class TimeMiliseconds24Validator(Adapter):
    def _decode(self, obj, content, path):
        return None if obj == 0xffffff else round(obj/1000, 3)

    def _encode(self, obj, content, path):
        return 0xffffff if obj is None else int(obj*1000)


class TimeExponential8Validator(Adapter):
    def _decode(self, obj, content, path):
        return round(pow(1.1, obj-64), 4) if obj else 0

    def _encode(self, obj, content, path):
        return round(log(obj, 1.1))+64 if obj else 0


class IlluminanceValidator(Adapter):
    def _decode(self, obj, content, path):
        return None if obj == 0xffffff else round(obj/100, 2)

    def _encode(self, obj, content, path):
        return 0xffffff if obj is None else int(obj*100)


class DefaultCountValidator(Adapter):
    def _decode(self, obj, content, path):
        return None if obj == (256**self.subcon.length)-1 else obj

    def _encode(self, obj, content, path):
        return (256**self.subcon.length)-1 if obj is None else obj


ElectricCurrent = Struct(
    "current" / ElectricCurrentValidator(Int16ul),
)

Voltage = Struct(
    "voltage" / VoltageValidator(Int16ul),
)

Presence = Struct(
    "presence_detected" / Flag
)

Percentage8 = Struct(
    "percentage" / Percentage8Validator(Int8ul)
)

TimeMiliseconds24 = Struct(
    "seconds" / TimeMiliseconds24Validator(Int24ul)
)

TimeHour24 = Struct(
    "hours" / DefaultCountValidator(Int24ul)
)

TimeSecond16 = Struct(
    "seconds" / DefaultCountValidator(Int16ul)
)

TimeExponential8 = Struct(
    "seconds" / TimeExponential8Validator(Int8ul)
)

AverageCurrent = Struct(
    "electric_current_value" / ElectricCurrentValidator(Int16ul),
    "sensing_duration" / TimeExponential8,
    Probe(this)
)

Illuminance = Struct(
    "illuminance" / IlluminanceValidator(Int24ul)
)

Count16 = Struct(
    "count" / DefaultCountValidator(Int16ul)
)

Count24 = Struct(
    "count" / DefaultCountValidator(Int24ul)
)

EventStatistics = Struct(
    "number_of_events" / Count16,
    "average_event_duration" / TimeSecond16,
    "time_elapsed_since_last_event" / TimeExponential8,
    "sensing_duration" / TimeExponential8,
)

Energy = Struct(
    "kilowatt_hour" / DefaultCountValidator(Int24ul)
)

PerceivedLightness = Struct(
    "perceived_lightness" / Int16ul
)


def FixedString(size):
    return Array(size, Byte)


PropertyValue = Switch(
    this.sensor_setting_property_id,
    {
        # PropertyID.AVERAGE_AMBIENT_TEMPERATURE_IN_A_PERIOD_OF_DAY = 0x0001
        PropertyID.AVERAGE_INPUT_CURRENT: AverageCurrent,
        # PropertyID.AVERAGE_INPUT_VOLTAGE = 0x0003
        PropertyID.AVERAGE_OUTPUT_CURRENT: AverageCurrent,
        # PropertyID.AVERAGE_OUTPUT_VOLTAGE = 0x0005
        # PropertyID.CENTER_BEAM_INTENSITY_AT_FULL_POWER = 0x0006
        # PropertyID.CHROMATICITY_TOLERANCE = 0x0007
        # PropertyID.COLOR_RENDERING_INDEX_R9 = 0x0008
        # PropertyID.COLOR_RENDERING_INDEX_RA = 0x0009
        # PropertyID.DEVICE_APPEARANCE = 0x000A
        # PropertyID.DEVICE_COUNTRY_OF_ORIGIN = 0x000B
        # PropertyID.DEVICE_DATE_OF_MANUFACTURE = 0x000C
        PropertyID.DEVICE_ENERGY_USE_SINCE_TURN_ON: Energy,
        PropertyID.DEVICE_FIRMWARE_REVISION: FixedString(8),
        # PropertyID.DEVICE_GLOBAL_TRADE_ITEM_NUMBER = 0x000F
        PropertyID.DEVICE_HARDWARE_REVISION: FixedString(16),
        PropertyID.DEVICE_MANUFACTURER_NAME: FixedString(36),
        PropertyID.DEVICE_MODEL_NUMBER: FixedString(24),
        # PropertyID.DEVICE_OPERATING_TEMPERATURE_RANGE_SPECIFICATION = 0x0013
        # PropertyID.DEVICE_OPERATING_TEMPERATURE_STATISTICAL_VALUES = 0x0014
        PropertyID.DEVICE_OVER_TEMPERATURE_EVENT_STATISTICS: EventStatistics,
        # PropertyID.DEVICE_POWER_RANGE_SPECIFICATION = 0x0016
        PropertyID.DEVICE_RUNTIME_SINCE_TURN_ON: TimeHour24,
        PropertyID.DEVICE_RUNTIME_WARRANTY: TimeHour24,
        PropertyID.DEVICE_SERIAL_NUMBER: FixedString(16),
        PropertyID.DEVICE_SOFTWARE_REVISION: FixedString(8),
        PropertyID.DEVICE_UNDER_TEMPERATURE_EVENT_STATISTICS: EventStatistics,
        # PropertyID.INDOOR_AMBIENT_TEMPERATURE_STATISTICAL_VALUES = 0x001C
        # PropertyID.INITIAL_CIE_1931_CHROMATICITY_COORDINATES = 0x001D
        # PropertyID.INITIAL_CORRELATED_COLOR_TEMPERATURE = 0x001E
        # PropertyID.INITIAL_LUMINOUS_FLUX = 0x001F
        # PropertyID.INITIAL_PLANCKIAN_DISTANCE = 0x0020
        # PropertyID.INPUT_CURRENT_RANGE_SPECIFICATION = 0x0021
        # PropertyID.INPUT_CURRENT_STATISTICS = 0x0022
        PropertyID.INPUT_OVER_CURRENT_EVENT_STATISTICS: EventStatistics,
        PropertyID.INPUT_OVER_RIPPLE_VOLTAGE_EVENT_STATISTICS: EventStatistics,
        PropertyID.INPUT_OVER_VOLTAGE_EVENT_STATISTICS: EventStatistics,
        PropertyID.INPUT_UNDER_CURRENT_EVENT_STATISTICS: EventStatistics,
        PropertyID.INPUT_UNDER_VOLTAGE_EVENT_STATISTICS: EventStatistics,
        # PropertyID.INPUT_VOLTAGE_RANGE_SPECIFICATION = 0x0028
        PropertyID.INPUT_VOLTAGE_RIPPLE_SPECIFICATION: Percentage8,
        # PropertyID.INPUT_VOLTAGE_STATISTICS = 0x002A
        PropertyID.LIGHT_CONTROL_AMBIENT_LUXLEVEL_ON: Illuminance,
        PropertyID.LIGHT_CONTROL_AMBIENT_LUXLEVEL_PROLONG: Illuminance,
        PropertyID.LIGHT_CONTROL_AMBIENT_LUXLEVEL_STANDBY: Illuminance,
        PropertyID.LIGHT_CONTROL_LIGHTNESS_ON: PerceivedLightness,
        PropertyID.LIGHT_CONTROL_LIGHTNESS_PROLONG: PerceivedLightness,
        PropertyID.LIGHT_CONTROL_LIGHTNESS_STANDBY: PerceivedLightness,
        PropertyID.LIGHT_CONTROL_REGULATOR_ACCURACY: Percentage8,
        # PropertyID.LIGHT_CONTROL_REGULATOR_KID = 0x0032
        # PropertyID.LIGHT_CONTROL_REGULATOR_KIU = 0x0033
        # PropertyID.LIGHT_CONTROL_REGULATOR_KPD = 0x0034
        # PropertyID.LIGHT_CONTROL_REGULATOR_KPU = 0x0035
        PropertyID.LIGHT_CONTROL_TIME_FADE: TimeMiliseconds24,
        PropertyID.LIGHT_CONTROL_TIME_FADE_ON: TimeMiliseconds24,
        PropertyID.LIGHT_CONTROL_TIME_FADE_STANDBY_AUTO: TimeMiliseconds24,
        PropertyID.LIGHT_CONTROL_TIME_FADE_STANDBY_MANUAL: TimeMiliseconds24,
        PropertyID.LIGHT_CONTROL_TIME_OCCUPANCY_DELAY: TimeMiliseconds24,
        PropertyID.LIGHT_CONTROL_TIME_PROLONG: TimeMiliseconds24,
        PropertyID.LIGHT_CONTROL_TIME_RUN_ON: TimeMiliseconds24,
        PropertyID.LUMEN_MAINTENANCE_FACTOR: Percentage8,
        # PropertyID.LUMINOUS_EFFICACY = 0x003E
        # PropertyID.LUMINOUS_ENERGY_SINCE_TURN_ON = 0x003F
        # PropertyID.LUMINOUS_EXPOSURE = 0x0040
        # PropertyID.LUMINOUS_FLUX_RANGE = 0x0041
        PropertyID.MOTION_SENSED: Percentage8,
        PropertyID.MOTION_THRESHOLD: Percentage8,
        PropertyID.OPEN_CIRCUIT_EVENT_STATISTICS: EventStatistics,
        # PropertyID.OUTDOOR_STATISTICAL_VALUES = 0x0045
        # PropertyID.OUTPUT_CURRENT_RANGE = 0x0046
        # PropertyID.OUTPUT_CURRENT_STATISTICS = 0x0047
        PropertyID.OUTPUT_RIPPLE_VOLTAGE_SPECIFICATION: Percentage8,
        # PropertyID.OUTPUT_VOLTAGE_RANGE = 0x0049
        # PropertyID.OUTPUT_VOLTAGE_STATISTICS = 0x004A
        PropertyID.OVER_OUTPUT_RIPPLE_VOLTAGE_EVENT_STATISTICS: EventStatistics,
        PropertyID.PEOPLE_COUNT: Count16,
        PropertyID.PRESENCE_DETECTED: Presence,
        PropertyID.PRESENT_AMBIENT_LIGHT_LEVEL: Illuminance,
        # PropertyID.PRESENT_AMBIENT_TEMPERATURE = 0x004F
        # PropertyID.PRESENT_CIE_1931_CHROMATICITY_COORDINATES = 0x0050
        # PropertyID.PRESENT_CORRELATED_COLOR_TEMPERATURE = 0x0051
        # PropertyID.PRESENT_DEVICE_INPUT_POWER = 0x0052 # TODO
        PropertyID.PRESENT_DEVICE_OPERATING_EFFICIENCY: Percentage8,
        # PropertyID.PRESENT_DEVICE_OPERATING_TEMPERATURE = 0x0054
        PropertyID.PRESENT_ILLUMINANCE: Illuminance,
        # PropertyID.PRESENT_INDOOR_AMBIENT_TEMPERATURE = 0x0056
        PropertyID.PRESENT_INPUT_CURRENT: ElectricCurrent,
        PropertyID.PRESENT_INPUT_RIPPLE_VOLTAGE: Percentage8,
        PropertyID.PRESENT_INPUT_VOLTAGE: Voltage,
        # PropertyID.PRESENT_LUMINOUS_FLUX = 0x005A
        # PropertyID.PRESENT_OUTDOOR_AMBIENT_TEMPERATURE = 0x005B
        PropertyID.PRESENT_OUTPUT_CURRENT: ElectricCurrent,
        PropertyID.PRESENT_OUTPUT_VOLTAGE: Voltage,
        # PropertyID.PRESENT_PLANCKIAN_DISTANCE = 0x005E
        PropertyID.PRESENT_RELATIVE_OUTPUT_RIPPLE_VOLTAGE: Percentage8,
        # PropertyID.RELATIVE_DEVICE_ENERGY_USE_IN_A_PERIOD_OF_DAY = 0x0060
        # PropertyID.RELATIVE_DEVICE_RUNTIME_IN_A_GENERIC_LEVEL_RANGE = 0x0061
        # PropertyID.RELATIVE_EXPOSURE_TIME_IN_AN_ILLUMINANCE_RANGE = 0x0062
        # PropertyID.RELATIVE_RUNTIME_IN_A_CORRELATED_COLOR_TEMPERATURE_RANGE = 0x0063
        # PropertyID.RELATIVE_RUNTIME_IN_A_DEVICE_OPERATING_TEMPERATURE_RANGE = 0x0064
        # PropertyID.RELATIVE_RUNTIME_IN_AN_INPUT_CURRENT_RANGE = 0x0065
        # PropertyID.RELATIVE_RUNTIME_IN_AN_INPUT_VOLTAGE_RANGE = 0x0066
        PropertyID.SHORT_CIRCUIT_EVENT_STATISTICS: EventStatistics,
        PropertyID.TIME_SINCE_MOTION_SENSED: TimeSecond16,
        PropertyID.TIME_SINCE_PRESENCE_DETECTED: TimeSecond16,
        PropertyID.TOTAL_DEVICE_ENERGY_USE: Energy,
        PropertyID.TOTAL_DEVICE_OFF_ON_CYCLES: Count24,
        PropertyID.TOTAL_DEVICE_POWER_ON_CYCLES: Count24,
        PropertyID.TOTAL_DEVICE_POWER_ON_TIME: TimeHour24,
        PropertyID.TOTAL_DEVICE_RUNTIME: TimeHour24,
        PropertyID.TOTAL_LIGHT_EXPOSURE_TIME: TimeHour24,
        # PropertyID.TOTAL_LUMINOUS_ENERGY = 0x0070
    }
)
