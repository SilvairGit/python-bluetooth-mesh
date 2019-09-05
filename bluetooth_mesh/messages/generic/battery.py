from construct import Int8ul, Int24ul, Struct, Switch, this, BitStruct, BitsInteger
from enum import IntEnum
from bluetooth_mesh.messages.util import EnumAdapter, Opcode, DefaultCountValidator


class GenericBatteryOpcode(IntEnum):
    BATTERY_GET = 0x8223
    BATTERY_STATUS = 0x8224


class GenericBatteryFlagsPresence(IntEnum):
    BATTERY_NOT_PRESENT = 0b00
    BATTERY_PRESENT_REMOVABLE = 0b01
    BATTERY_PRESENT_NON_REMOVABLE = 0b10
    BATTERY_PRESENCE_UNKNOWN = 0b11


class GenericBatteryFlagsIndicator(IntEnum):
    BATTERY_CHARGE_CRITICALLY_LOW = 0b00
    BATTERY_CHARGE_LOW = 0b01
    BATTERY_CHARGE_GOOD = 0b10
    BATTERY_CHARGE_UNKNOWN = 0b11


class GenericBatteryFlagsCharging(IntEnum):
    BATTERY_NOT_CHARGEABLE = 0b00
    BATTERY_CHARGEABLE_NOT_CHARGING = 0b01
    BATTERY_CHARGEABLE_CHARGING = 0b10
    BATTERY_CHARGING_STATE_UNKNOWN = 0b11


class GenericBatteryFlagsServiceability(IntEnum):
    RFU = 0b00
    BATTERY_NOT_REQUIRE_SERVICE = 0b01
    BATTERY_REQUIRE_SERVICE = 0b10
    BATTERY_SERVICEABILITY_UNKNOWN = 0b11


BatteryFlags = BitStruct(
    "battery_serviceability_flags" / EnumAdapter(BitsInteger(2),
                                                 GenericBatteryFlagsServiceability),
    "battery_charging_flags" / EnumAdapter(BitsInteger(2),
                                           GenericBatteryFlagsCharging),
    "battery_indicator_flags" / EnumAdapter(BitsInteger(2),
                                            GenericBatteryFlagsIndicator),
    "battery_presence_flags" / EnumAdapter(BitsInteger(2),
                                           GenericBatteryFlagsPresence),
)

GenericBatteryGet = Struct()

GenericBatteryStatus = Struct(
    "battery_level" / DefaultCountValidator(Int8ul),
    "time_to_discharge" / DefaultCountValidator(Int24ul),
    "time_to_charge" / DefaultCountValidator(Int24ul),
    "flags" / BatteryFlags
)

GenericBatteryMessage = Struct(
    "opcode" / EnumAdapter(Opcode, GenericBatteryOpcode),
    "params" / Switch(
        this.opcode,
        {
            GenericBatteryOpcode.BATTERY_GET: GenericBatteryGet,
            GenericBatteryOpcode.BATTERY_STATUS: GenericBatteryStatus,
        },
    )
)
