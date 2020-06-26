#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
from enum import IntEnum

from construct import (
    Array,
    BitsInteger,
    Byte,
    Const,
    Embedded,
    ExprAdapter,
    GreedyRange,
    Int8ul,
    Int16ul,
    Select,
    Struct,
    Switch,
    obj_,
    this,
)

from bluetooth_mesh.messages.config import DoubleKeyIndex, EmbeddedBitStruct
from bluetooth_mesh.messages.properties import DefaultCountValidator, PropertyValue
from bluetooth_mesh.messages.util import EnumAdapter, Opcode, OpcodeMessage


class SensorSampling(IntEnum):
    UNSPECIFIED = 0x00
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

    def __repr__(self):
        return str(self.value)


class SensorSetupOpcode(IntEnum):
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

    def __repr__(self):
        return str(self.value)


# fmt: off
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

SensorSettingStatus = Struct(
    Embedded(SensorSettingGet),
    "sensor_setting_access" / Int8ul,
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

MarshalledPropertyIDShort = EmbeddedBitStruct(
    "_",
    "sensor_setting_property_id" / BitsInteger(11),
    "length" / ExprAdapter(BitsInteger(4), obj_ + 1, obj_ - 1),
    "format" / Const(0, BitsInteger(1)),
    reversed=True
)

MarshalledPropertyIDLong = EmbeddedBitStruct(
    "_",
    "sensor_setting_property_id" / BitsInteger(16),
    "length" / ExprAdapter(BitsInteger(7), obj_ + 1, obj_ - 1),
    "format" / Const(1, BitsInteger(1)),
    reversed=True
)

SensorData = Select(
    Struct(
        *MarshalledPropertyIDShort,
        "sensor_setting_raw" / PropertyValue,
    ),
    Struct(
        *MarshalledPropertyIDLong,
        "sensor_setting_raw" / Array(this.length, Byte),
    )
)

SensorStatus = GreedyRange(
    SensorData
)

# TODO: message not implemented due to somewhat complicated structure and lack of examples
# SensorColumnGet = Struct(
#     Embedded(SensorSettingsGet),
#     "raw_value_x" / PropertyValue
# )

# TODO: message not implemented due to somewhat complicated structure and lack of examples
# SensorSeriesGet = Struct(
#     Embedded(SensorSettingsGet),
#     "raw_value_y" / PropertyValue
# )

FastCadencePeriodDivisorAndTriggerType = EmbeddedBitStruct(
    "status_trigger_type" / BitsInteger(1),
    "fast_cadence_period_divisor" / BitsInteger(7)
)

UnitlessTriggerDelta = DefaultCountValidator(Int8ul, rounding=1, resolution=0.1)

TriggerDelta = Struct(
    Switch(
        this.status_trigger_type,
        {
            0: Struct(
                "status_trigger_delta_down" / PropertyValue,
                "status_trigger_delta_up" / PropertyValue
            ),
            1: Struct(
                "status_trigger_delta_down" / UnitlessTriggerDelta,
                "status_trigger_delta_up" / UnitlessTriggerDelta
            )
        }
    )
)

# TODO: message not implemented due to somewhat complicated structure and lack of examples
# SensorCadence = Struct(
#     "sensor_setting_property_id" / Int16ul,
#     *FastCadencePeriodDivisorAndTriggerType,
#     Embedded(TriggerDelta),
#     "status_min_interval" / ExprAdapter(Int16ul, lambda obj, ctx: pow(2, obj), lambda obj, ctx: log(obj, 2)),
#     "fast_cadence_low" / PropertyValue,
#     "fast_cadence_high" / PropertyValue
# )

SensorMessage = OpcodeMessage({
    SensorOpcode.SENSOR_DESCRIPTOR_GET: SensorGet,
    SensorOpcode.SENSOR_DESCRIPTOR_STATUS: SensorDescriptorStatus,
    SensorOpcode.SENSOR_GET: SensorGet,
    SensorOpcode.SENSOR_STATUS: SensorStatus,
    # SensorOpcode.SENSOR_COLUMN_GET: SensorColumnGet,
    # SensorOpcode.SENSOR_COLUMN_STATUS: 0x00,
    # SensorOpcode.SENSOR_SERIES_GET: SensorSeriesGet,
    # SensorOpcode.SENSOR_SERIES_STATUS: 0x00,
})


SensorSetupMessage = OpcodeMessage({
    SensorSetupOpcode.SENSOR_CADENCE_GET: SensorGetOptional,
    # SensorSetupOpcode.SENSOR_CADENCE_SET: SensorCadence,
    # SensorSetupOpcode.SENSOR_CADENCE_SET_UNACKNOWLEDGED: SensorCadence,
    # SensorSetupOpcode.SENSOR_CADENCE_STATUS: SensorCadence,
    SensorSetupOpcode.SENSOR_SETTINGS_GET: SensorSettingsGet,
    SensorSetupOpcode.SENSOR_SETTINGS_STATUS: SensorSettingsStatus,
    SensorSetupOpcode.SENSOR_SETTING_GET: SensorSettingGet,
    SensorSetupOpcode.SENSOR_SETTING_SET: SensorSettingSet,
    SensorSetupOpcode.SENSOR_SETTING_SET_UNACKNOWLEDGED: SensorSettingSet,
    SensorSetupOpcode.SENSOR_SETTING_STATUS: SensorSettingStatus,
})
# fmt: on
