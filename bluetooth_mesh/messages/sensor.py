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
import io
from enum import IntEnum

from construct import (
    Array,
    BitsInteger,
    Byte,
    Const,
    Construct,
    Container,
    Embedded,
    ExprAdapter,
    GreedyRange,
    Int8ul,
    Int16ul,
    Select,
    Struct,
    Switch,
    obj_,
    stream_read,
    stream_read_entire,
    stream_write,
    this,
)

from bluetooth_mesh.messages.config import DoubleKeyIndex, EmbeddedBitStruct
from bluetooth_mesh.messages.properties import (
    DefaultCountValidator,
    PropertyDict,
    PropertyID,
    PropertyValue,
)
from bluetooth_mesh.messages.util import (
    AliasedContainer,
    EnumAdapter,
    FieldAdapter,
    NamedSelect,
    Opcode,
    SwitchStruct,
)


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
SensorPropertyId = FieldAdapter(
    Select(
        EnumAdapter(Int16ul, PropertyID),
        Int16ul),
    Int16ul
)

SensorGetMinimal = Struct()

SensorGetOptional = Struct(
    "property_id" / SensorPropertyId,
)

SensorGet = NamedSelect(
    optional=SensorGetOptional,
    minimal=SensorGetMinimal
)

SensorSettingsGet = Struct(
    "sensor_property_id" / SensorPropertyId,
)

SensorSettingGet = Struct(
    Embedded(SensorSettingsGet),
    "sensor_setting_property_id" / SensorPropertyId,
)

class SensorSettingRawMixin:
    def _parse_sensor_setting(self, stream, context, path, sensor_setting_property_id, **kwargs):
        try:
            sensor_setting_property_id = PropertyID(sensor_setting_property_id)
            sensor_setting_name = sensor_setting_property_id.name.lower()
        except ValueError:
            sensor_setting_name = "sensor_setting_raw"

        try:
            sensor_setting_raw = PropertyDict[sensor_setting_property_id]._parse(stream, context, path)
        except KeyError:
            sensor_setting_raw = list(stream_read_entire(stream))

        class _Container(AliasedContainer):
            ALIAS = sensor_setting_name
            ORIGINAL = "sensor_setting_raw"

        return _Container({
            **kwargs,
            "sensor_setting_property_id": sensor_setting_property_id,
            sensor_setting_name: sensor_setting_raw
        })

    def _build_sensor_setting(self, obj, stream, context, path, sensor_setting_property_id):
        try:
            sensor_setting_property_id = PropertyID(sensor_setting_property_id)
            sensor_setting_name = sensor_setting_property_id.name.lower()
        except ValueError:
            sensor_setting_name = "sensor_setting_raw"

        sensor_setting_raw = obj.get(sensor_setting_name, obj.get("sensor_setting_raw"))

        try:
            PropertyDict[sensor_setting_property_id]._build(sensor_setting_raw, stream, context, path)
        except KeyError:
            stream_write(stream, bytes(sensor_setting_raw))

        return obj


class _SensorSettingSet(SensorSettingRawMixin, Construct):
    subcon = Struct(
        "sensor_property_id" / SensorPropertyId,
        "sensor_setting_property_id" / SensorPropertyId,
        PropertyValue,
    )

    def _parse(self, stream, context, path):
        obj = SensorSettingGet._parse(stream, context, path)

        sensor_setting_property_id = obj.pop("sensor_setting_property_id")
        return self._parse_sensor_setting(stream, context, path, sensor_setting_property_id, **obj)

    def _build(self, obj, stream, context, path):
        SensorSettingGet._build(obj, stream, context, path)

        sensor_setting_property_id = obj["sensor_setting_property_id"]
        return self._build_sensor_setting(obj, stream, context, path, sensor_setting_property_id)


SensorSettingSet = _SensorSettingSet()


class _SensorSettingStatus(SensorSettingRawMixin, Construct):
    subcon = Struct(
        "sensor_property_id" / SensorPropertyId,
        "sensor_setting_property_id" / SensorPropertyId,
        "sensor_setting_access" / Int8ul,
        PropertyValue,
    )

    def _parse(self, stream, context, path):
        obj = Struct(Embedded(SensorSettingGet), "sensor_setting_access" / Int8ul)._parse(stream, context, path)

        sensor_setting_property_id = obj.pop("sensor_setting_property_id")
        return self._parse_sensor_setting(stream, context, path, sensor_setting_property_id, **obj)

    def _build(self, obj, stream, context, path):
        Struct(Embedded(SensorSettingGet), "sensor_setting_access" / Int8ul)._build(obj, stream, context, path)

        sensor_setting_property_id = obj["sensor_setting_property_id"]
        return self._build_sensor_setting(obj, stream, context, path, sensor_setting_property_id)


SensorSettingStatus = _SensorSettingStatus()

SensorSettingsStatus = Struct(
    Embedded(SensorSettingsGet),
    "sensor_setting_property_ids" / GreedyRange(SensorPropertyId)
)

SensorDescriptorMinimal = Struct(
    "sensor_property_id" / SensorPropertyId,
)

SensorDescriptorOptional = Struct(
    Embedded(SensorDescriptorMinimal),
    *DoubleKeyIndex("sensor_negative_tolerance", "sensor_positive_tolerance"),
    "sensor_sampling_funcion" / Int8ul,
    "sensor_measurement_period" / Int8ul,
    "sensor_update_interval" / Int8ul
)

SensorDescriptorStatusItem = NamedSelect(
    optional=SensorDescriptorOptional,
    minimal=SensorDescriptorMinimal
)

SensorDescriptorStatus = GreedyRange(SensorDescriptorStatusItem)

class _SensorData(SensorSettingRawMixin, Construct):
    subcon = Struct(
        "format" / Int8ul,
        "length" / Int16ul,
        "sensor_setting_property_id" / SensorPropertyId,
        PropertyValue,
    )

    def _parse(self, stream, context, path):
        setting_property_id = stream_read(stream, 2)

        format = setting_property_id[0] & 0x01

        if format:
            setting_property_id += stream_read(stream, 1)

            length = (setting_property_id[0] >> 1) + 1
            sensor_setting_property_id = setting_property_id[1] | setting_property_id[2] << 8
        else:
            length = ((setting_property_id[0] >> 1) & 0b1111) + 1
            sensor_setting_property_id = (setting_property_id[0] >> 5 & 0b111) | setting_property_id[1] << 3

        substream = io.BytesIO(stream.read(length))
        return self._parse_sensor_setting(substream, context, path, sensor_setting_property_id, format=format, length=length)

    def _build(self, obj, stream, context, path):
        sensor_setting_property_id = obj["sensor_setting_property_id"]

        format = obj["format"]
        length = obj["length"]

        if format:
            stream_write(stream, bytes([(length - 1) << 1 | 0x01]))
            stream_write(stream, sensor_setting_property_id.to_bytes(2, byteorder='little'))
        else:
            stream_write(stream, bytes([(length - 1) << 1 | (sensor_setting_property_id & 0b111) << 5]))
            stream_write(stream, bytes([sensor_setting_property_id >> 3]))

        return self._build_sensor_setting(obj, stream, context, path, sensor_setting_property_id)

SensorData = _SensorData()

SensorStatus = GreedyRange(SensorData)

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

SensorMessage = SwitchStruct(
    "opcode" / Opcode(SensorOpcode),
    "params" / Switch(
        this.opcode,
        {
            SensorOpcode.SENSOR_DESCRIPTOR_GET: SensorGet,
            SensorOpcode.SENSOR_DESCRIPTOR_STATUS: SensorDescriptorStatus,
            SensorOpcode.SENSOR_GET: SensorGet,
            SensorOpcode.SENSOR_STATUS: SensorStatus,
            # SensorOpcode.SENSOR_COLUMN_GET: SensorColumnGet,
            # SensorOpcode.SENSOR_COLUMN_STATUS: 0x00,
            # SensorOpcode.SENSOR_SERIES_GET: SensorSeriesGet,
            # SensorOpcode.SENSOR_SERIES_STATUS: 0x00,
        }
    )
)

SensorSetupMessage = SwitchStruct(
    "opcode" / Opcode(SensorSetupOpcode),
    "params" / Switch(
        this.opcode,
        {
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
        }
    )
)
# fmt: on
