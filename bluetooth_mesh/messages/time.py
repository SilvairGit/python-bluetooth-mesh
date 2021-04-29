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
import calendar
import enum
import time
from datetime import datetime, timedelta, timezone

from construct import (
    Adapter,
    BitsInteger,
    BytesInteger,
    Construct,
    Container,
    Flag,
    Int8ul,
    Padding,
    StopIf,
    Struct,
    stream_read,
    stream_write,
    this,
)

from bluetooth_mesh.messages.util import EmbeddedBitStruct, EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import NamedSelect, Opcode, SwitchStruct

MS_IN_UNCERTAINTY_STEP = 10
UNCERTAINTY_MS = 10
CURRENT_TAI_UTC_DELTA = 37
TAI_UTC_DELTA_ZERO = 0xFF
TIME_ZONE_OFFSET_ZERO = 0x40
MESH_UNIX_EPOCH_DIFF = calendar.timegm(
    time.strptime("2000-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
) - calendar.timegm(time.gmtime(0))
SECONDS_IN_15_MINUTES = 15 * 60


# fmt: off


class TimeRole(enum.IntEnum):
    NONE = 0
    TIME_AUTHORITY = 1
    TIME_RELAY = 2
    TIME_CLIENT = 3


def TAI_UTC_DeltaPaddedField(tai_utc_delta_name: str):
    return EmbeddedBitStruct("_",
                             Padding(1),
                             tai_utc_delta_name / BitsInteger(15),
                             reversed=True
                             )


def mesh_time_zone_offset_to_timedelta(time_zone_offset: int) -> timedelta:
    return timedelta(seconds=(time_zone_offset - TIME_ZONE_OFFSET_ZERO) * SECONDS_IN_15_MINUTES)


def timedelta_to_mesh_time_zone_offset(time_zone: timedelta) -> int:
    if time_zone is None:
        return TIME_ZONE_OFFSET_ZERO

    assert (int(time_zone.total_seconds() % SECONDS_IN_15_MINUTES) == 0)
    return int((time_zone.total_seconds() // SECONDS_IN_15_MINUTES) + TIME_ZONE_OFFSET_ZERO)


def mesh_tai_utc_delta_to_timedelta(tai_utc_delta: int) -> timedelta:
    return timedelta(seconds=tai_utc_delta - TAI_UTC_DELTA_ZERO)


def timedelta_to_mesh_tai_utc_delta(time_zone: timedelta) -> int:
    assert (time_zone.total_seconds().is_integer())
    return int(time_zone.total_seconds() + TAI_UTC_DELTA_ZERO)


def subsecond_to_seconds(subsecond: int) -> float:
    return subsecond / 256


def seconds_to_subsecond(seconds: float) -> int:
    return round((seconds - int(seconds)) * 256)

TimeMinimal = Struct(
    "tai_seconds" / BytesInteger(5, swapped=True),
)

TimeOptional = Struct(
    "tai_seconds" / BytesInteger(5, swapped=True),
    StopIf(this.tai_seconds == 0),
    "subsecond" / Int8ul,
    "uncertainty" / Int8ul,
    *EmbeddedBitStruct("_",
                       "tai_utc_delta" / BitsInteger(15),
                       "time_authority" / Flag,
                       reversed=True
                       ),
    "time_zone_offset" / Int8ul,
)

Time = NamedSelect(
    optional=TimeOptional,
    minimal=TimeMinimal,
)


class TimeAdapter(Adapter):
    def _decode(self, obj, context, path):
        if obj["tai_seconds"] == 0:
            return Container(
                date=None,
                tai_utc_delta=None,
                time_authority=None,
                uncertainty=None
            )
        time_zone = mesh_time_zone_offset_to_timedelta(obj["time_zone_offset"])
        full_recv_time = obj["tai_seconds"] + subsecond_to_seconds(obj["subsecond"]) + MESH_UNIX_EPOCH_DIFF + int(
            time_zone.total_seconds())
        recv_date = datetime.fromtimestamp(full_recv_time, timezone(time_zone))

        return Container(
            date=recv_date,
            tai_utc_delta=mesh_tai_utc_delta_to_timedelta(obj["tai_utc_delta"]),
            time_authority=bool(obj["time_authority"]),
            uncertainty=timedelta(milliseconds=(obj["uncertainty"] * 10))
        )

    def _encode(self, obj, context, path):
        passed_time: datetime = obj["date"]
        total_time = passed_time.timestamp() - MESH_UNIX_EPOCH_DIFF - passed_time.utcoffset().total_seconds()

        return Container(
            tai_seconds=int(total_time),
            subsecond=seconds_to_subsecond(total_time),
            uncertainty=int((obj["uncertainty"].total_seconds() * 100)),
            tai_utc_delta=timedelta_to_mesh_tai_utc_delta(obj["tai_utc_delta"]),
            time_authority=bool(obj["time_authority"]),
            time_zone_offset=timedelta_to_mesh_time_zone_offset(passed_time.utcoffset())
        )


TimeRoleMsg = Struct(
    "time_role" / EnumAdapter(Int8ul, TimeRole)
)

TimeGet = Struct()

TimeSet = TimeAdapter(Time)

TimeStatus = TimeAdapter(Time)

TimeZoneGet = Struct()

TimeZoneSet = Struct(
    "time_zone_offset_new" / Int8ul,
    "tai_of_zone_change" / BytesInteger(5, swapped=True),
)

TimeZoneStatus = Struct(
    "time_zone_offset_current" / Int8ul,
    "time_zone_offset_new" / Int8ul,
    "tai_of_zone_change" / BytesInteger(5, swapped=True),
)

TAIUTCDeltaGet = Struct()

TAIUTCDeltaSet = Struct(
    *TAI_UTC_DeltaPaddedField("tai_utc_delta_new"),
    "tai_of_delta_change" / BytesInteger(5, swapped=True),
)

TAIUTCDeltaStatus = Struct(
    *TAI_UTC_DeltaPaddedField("tai_utc_delta_current"),
    *TAI_UTC_DeltaPaddedField("tai_utc_delta_new"),
    "tai_of_delta_change" / BytesInteger(5, swapped=True),
)

TimeRoleGet = Struct()

TimeRoleSet = TimeRoleMsg

TimeRoleStatus = TimeRoleMsg


# fmt: off

class TimeOpcode(enum.IntEnum):
    TIME_GET = 0x8237
    TIME_SET = 0x005C
    TIME_STATUS = 0x005D
    TIME_ROLE_GET = 0x8238
    TIME_ROLE_SET = 0x8239
    TIME_ROLE_STATUS = 0x823A
    TIME_ZONE_GET = 0x823B
    TIME_ZONE_SET = 0x823C
    TIME_ZONE_STATUS = 0x823D
    TAI_UTC_DELTA_GET = 0x823E
    TAI_UTC_DELTA_SET = 0x823F
    TAI_UTC_DELTA_STATUS = 0x8240


# fmt: off
TimeMessage = SwitchStruct(
    "opcode" / Opcode(TimeOpcode),
    "params" / Switch(
        this.opcode,
        {
            TimeOpcode.TIME_GET: TimeGet,
            TimeOpcode.TIME_SET: TimeSet,
            TimeOpcode.TIME_STATUS: TimeStatus,
            TimeOpcode.TIME_ZONE_GET: TimeZoneGet,
            TimeOpcode.TIME_ZONE_SET: TimeZoneSet,
            TimeOpcode.TIME_ZONE_STATUS: TimeZoneStatus,
            TimeOpcode.TAI_UTC_DELTA_GET: TAIUTCDeltaGet,
            TimeOpcode.TAI_UTC_DELTA_SET: TAIUTCDeltaSet,
            TimeOpcode.TAI_UTC_DELTA_STATUS: TAIUTCDeltaStatus,
            TimeOpcode.TIME_ROLE_GET: TimeRoleGet,
            TimeOpcode.TIME_ROLE_SET: TimeRoleSet,
            TimeOpcode.TIME_ROLE_STATUS: TimeRoleStatus
        }
    )
)
# fmt: on
