from construct import Default, Int8ul, Int16ul, Int24ul, Int32ul, Select, Struct, Switch, Optional, this, Embedded, GreedyRange, Probe, EmbeddedSwitch
from enum import IntEnum
from bluetooth_mesh.messages.util import EnumAdapter, Opcode
from bluetooth_mesh.messages.config import DoubleKeyIndex
from bluetooth_mesh.messages.properties import PropertyValue, PropertyID, ElectricCurrent


class SensorSampling(IntEnum):
    UNSPECIFIED = 0X00
    INSTANTANEOUS = 0x01
    ARITHMETIC_MEAN = 0x02
    RMS = 0x03
    MAXIMUM = 0x04
    MINIMUM = 0x05
    ACCUMULATED = 0x06
    COUNT = 0x07


class SensorSettingAccess(IntEnum):
    READ_ONLY = 0x01
    READ_WRITE = 0x03


class SensorOpcode(IntEnum):
    SENSOR_DESCRIPTOR_GET = 0x8230
    SENSOR_DESCRIPTOR_STATUS = 0x51
    SENSOR_GET = 0x8231
    SENSOR_STATUS = 0x52
    SENSOR_COLUMN_GET = 0x8232
    SENSOR_COLUMN_STATUS = 0x53
    SENSOR_SERIES_GET = 0x8233
    SENSOR_SERIES_STATUS = 0x54

    # sensor setup
    SENSOR_CADENCE_GET = 0x8234
    SENSOR_CADENCE_SET = 0x55
    SENSOR_CADENCE_SET_UNACKNOWLEDGED = 0x56
    SENSOR_CADENCE_STATUS = 0x57
    SENSOR_SETTINGS_GET = 0x8235
    SENSOR_SETTINGS_STATUS = 0x58
    SENSOR_SETTING_GET = 0x8236
    SENSOR_SETTING_SET = 0x59
    SENSOR_SETTING_SET_UNACKNOWLEDGED = 0x5A
    SENSOR_SETTING_STATUS = 0x5B


SensorGetMinimal = Struct()

SensorGetOptional = Struct(
    "property_id" / Int16ul
)

SensorGet = Select(
    SensorGetOptional,
    SensorGetMinimal
)

SensorSettingsGet = Struct(
    "sensor_property_id" / Int16ul
)

SensorSettingGet = Struct(
    Embedded(SensorSettingsGet),
    "sensor_setting_property_id" / Int16ul
)

SensorSettingSet = Struct(
    Embedded(SensorSettingGet),
    "sensor_setting_raw" / PropertyValue,
)

SensorSettingsStatus = Struct(
    Embedded(SensorSettingsGet),
    "sensor_setting_property_ids" / GreedyRange(Int16ul)
)

SensorDescriptor = Struct(
    "sensor_property_id" / Int16ul,
    *DoubleKeyIndex("sensor_negative_tolerance", "sensor_positive_tolerance"),
    "sensor_sampling_funcion" / Int8ul,
    "sensor_measurement_period" / Int8ul,
    "sensor_update_interval" / Int8ul
)

SensorDescriptorStatus = GreedyRange(
    Select(
        SensorDescriptor,
        Struct("sensor_property_id" / Int16ul)
    ),
)

SensorColumnGet = Struct(
    Embedded(SensorSettingsGet),
    "raw_value_x" / GreedyRange(Int8ul)
)


SensorMessage = Struct(
    "opcode" / EnumAdapter(Opcode, SensorOpcode),
    "params" / Switch(
        this.opcode,
        {
            SensorOpcode.SENSOR_DESCRIPTOR_GET: SensorGet,
            SensorOpcode.SENSOR_DESCRIPTOR_STATUS: SensorDescriptorStatus,
            SensorOpcode.SENSOR_GET: SensorGet,
            # SensorOpcode.SENSOR_STATUS: 0x00,
            SensorOpcode.SENSOR_COLUMN_GET: SensorColumnGet,
            # SensorOpcode.SENSOR_COLUMN_STATUS: 0x00,
            # SensorOpcode.SENSOR_SERIES_GET: SensorSeriesGet,
            # SensorOpcode.SENSOR_SERIES_STATUS: 0x00,

            # # sensor setup
            SensorOpcode.SENSOR_CADENCE_GET: SensorGetOptional,
            # SensorOpcode.SENSOR_CADENCE_SET: 0x55,
            # SensorOpcode.SENSOR_CADENCE_SET_UNACKNOWLEDGED: 0x56,
            # SensorOpcode.SENSOR_CADENCE_STATUS: 0x57,
            SensorOpcode.SENSOR_SETTINGS_GET: SensorSettingsGet,
            SensorOpcode.SENSOR_SETTINGS_STATUS: SensorSettingsStatus,
            SensorOpcode.SENSOR_SETTING_GET: SensorSettingGet,
            SensorOpcode.SENSOR_SETTING_SET: SensorSettingSet,
            SensorOpcode.SENSOR_SETTING_SET_UNACKNOWLEDGED: SensorSettingSet,
            # SensorOpcode.SENSOR_SETTING_STATUS: 0x5B
        },
    )
)
