import pytest

from bluetooth_mesh.messages.sensor import (
    SensorMessage, SensorOpcode, PropertyID
)
from bluetooth_mesh.messages.config import StatusCode


valid = [
    pytest.param(
        b'\x82\x30',
        SensorOpcode.SENSOR_DESCRIPTOR_GET,
        dict(),
        id="SENSOR_DESCRIPTOR_GET"),
    pytest.param(
        b'\x82\x30\x04\x00',
        SensorOpcode.SENSOR_DESCRIPTOR_GET,
        dict(property_id=PropertyID.AVERAGE_OUTPUT_CURRENT),
        id="SENSOR_DESCRIPTOR_GET_with_optional"),
    pytest.param(
        b'\x82\x31',
        SensorOpcode.SENSOR_GET,
        dict(),
        id="SENSOR_GET"),
    pytest.param(
        b'\x82\x31\x07\x00',
        SensorOpcode.SENSOR_GET,
        dict(property_id=PropertyID.CHROMATICITY_TOLERANCE),
        id="SENSOR_GET_with_optional"),

    pytest.param(
        b'\x51\x0c\x00\x00\x00\x00\x0a\x0b\x0c',
        SensorOpcode.SENSOR_DESCRIPTOR_STATUS,
        [dict(sensor_property_id=PropertyID.DEVICE_DATE_OF_MANUFACTURE,
              sensor_positive_tolerance=0x00,
              sensor_negative_tolerance=0x00,
              sensor_sampling_funcion=0x0a,
              sensor_measurement_period=0x0b,
              sensor_update_interval=0x0c)],
        id="SENSOR_DESCRIPTOR_STATUS"),
    pytest.param(
        b'\x51\x19\x00',
        SensorOpcode.SENSOR_DESCRIPTOR_STATUS,
        [dict(sensor_property_id=PropertyID.DEVICE_SERIAL_NUMBER)],
        id="SENSOR_DESCRIPTOR_STATUS_not_existing"),
    pytest.param(
        b'\x51\x0c\x00\x00\x00\x00\x0a\x0b\x0c\x1f\x00\xef\xcd\xab\x1a\x1b\x1c',
        SensorOpcode.SENSOR_DESCRIPTOR_STATUS,
        [dict(sensor_property_id=PropertyID.DEVICE_DATE_OF_MANUFACTURE,
              sensor_positive_tolerance=0x00,
              sensor_negative_tolerance=0x00,
              sensor_sampling_funcion=0x0a,
              sensor_measurement_period=0x0b,
              sensor_update_interval=0x0c),
         dict(sensor_property_id=PropertyID.INITIAL_LUMINOUS_FLUX,
              sensor_positive_tolerance=0xabc,
              sensor_negative_tolerance=0xdef,
              sensor_sampling_funcion=0x1a,
              sensor_measurement_period=0x1b,
              sensor_update_interval=0x1c)],
        id="SENSOR_DESCRIPTOR_STATUS_multiple"),

    pytest.param(
        b'\x58\x30\x00\x01\x00\x04\x00\x09\x00',
        SensorOpcode.SENSOR_SETTINGS_STATUS,
        dict(sensor_property_id=PropertyID.LIGHT_CONTROL_LIGHTNESS_STANDBY,
             sensor_setting_property_ids=[1, 4, 9]),
        id="SENSOR_SETTINGS_STATUS"),
    pytest.param(
        b'\x58\x30\x00',
        SensorOpcode.SENSOR_SETTINGS_STATUS,
        dict(sensor_property_id=PropertyID.LIGHT_CONTROL_LIGHTNESS_STANDBY,
             sensor_setting_property_ids=[]),
        id="SENSOR_SETTING_SET_empty"),

    pytest.param(
        b'\x59\x57\x00\x57\x00\xc8\x00',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_raw=dict(
                 current=2.0)),
        id="SENSOR_SETTING_SET"),
]

valid_properties = [
    pytest.param(
        b'\x59\x57\x00\x57\x00\xc8\x00',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_raw=dict(
                 current=2.0)),
        id="ElectricCurrent"),
    pytest.param(
        b'\x59\x57\x00\x02\x00\xc8\x00\x39',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_property_id=PropertyID.AVERAGE_INPUT_CURRENT,
             sensor_setting_raw=dict(
                 electric_current_value=2.0,
                 sensing_duration=dict(seconds=0.5132))),
        id="AverageCurrent"),
    pytest.param(
        b'\x59\x57\x00\x02\x00\xc8\x00\x00',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_property_id=PropertyID.AVERAGE_INPUT_CURRENT,
             sensor_setting_raw=dict(
                 electric_current_value=2.0,
                 sensing_duration=dict(seconds=0))),
        id="AverageCurrent_with_0"),
    pytest.param(
        b'\x59\x59\x00\x59\x00\x00\x03',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_VOLTAGE,
             sensor_setting_property_id=PropertyID.PRESENT_INPUT_VOLTAGE,
             sensor_setting_raw=dict(
                 voltage=12)),
        id="Voltage"),
    pytest.param(
        b'\x59\x42\x00\x4d\x00\x01',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.MOTION_SENSED,
             sensor_setting_property_id=PropertyID.PRESENCE_DETECTED,
             sensor_setting_raw=dict(
                 presence_detected=True)),
        id="Presence"),
    pytest.param(
        b'\x59\x42\x00\x42\x00\x50',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.MOTION_SENSED,
             sensor_setting_property_id=PropertyID.MOTION_SENSED,
             sensor_setting_raw=dict(
                 percentage=40)),
        id="Percentage8"),
    pytest.param(
        b'\x59\x0a\x00\x36\x00\xb8\x0b\x00',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.DEVICE_APPEARANCE,
             sensor_setting_property_id=PropertyID.LIGHT_CONTROL_TIME_FADE,
             sensor_setting_raw=dict(
                 seconds=3)),
        id="TimeMiliseconds24"),
    pytest.param(
        b'\x59\x6d\x00\x6d\x00\x0a\x00\x00',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_TIME,
             sensor_setting_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_TIME,
             sensor_setting_raw=dict(
                 hours=10)),
        id="TimeHour24"),
    pytest.param(
        b'\x59\x6d\x00\x6d\x00\xff\xff\xff',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_TIME,
             sensor_setting_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_TIME,
             sensor_setting_raw=dict(
                 hours=None)),
        id="TimeHour24_unknown"),
    pytest.param(
        b'\x59\x55\x00\x55\x00\x1a\x27\x00',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.PRESENT_ILLUMINANCE,
             sensor_setting_property_id=PropertyID.PRESENT_ILLUMINANCE,
             sensor_setting_raw=dict(
                 illuminance=100.1)),
        id="Illuminance"),
    pytest.param(
        b'\x59\x4c\x00\x4c\x00\x1b\x1a',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.PEOPLE_COUNT,
             sensor_setting_property_id=PropertyID.PEOPLE_COUNT,
             sensor_setting_raw=dict(
                 count=0x1a1b)),
        id="Count16"),
    pytest.param(
        b'\x59\x6c\x00\x6c\x00\xff\x1b\x1a',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_CYCLES,
             sensor_setting_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_CYCLES,
             sensor_setting_raw=dict(
                 count=0x1a1bff)),
        id="Count24"),
    pytest.param(
        b'\x59\x6c\x00\x6c\x00\xff\xff\xff',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_CYCLES,
             sensor_setting_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_CYCLES,
             sensor_setting_raw=dict(
                 count=None)),
        id="Count24_unknown"),
    pytest.param(
        b'\x59\x68\x00\x68\x00\x05\x00',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.TIME_SINCE_MOTION_SENSED,
             sensor_setting_property_id=PropertyID.TIME_SINCE_MOTION_SENSED,
             sensor_setting_raw=dict(
                 seconds=5)),
        id="TimeSecond16"),
    pytest.param(
        b'\x59\x67\x00\x67\x00\x05\x00\x01\x00\x70\x40',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.SHORT_CIRCUIT_EVENT_STATISTICS,
             sensor_setting_property_id=PropertyID.SHORT_CIRCUIT_EVENT_STATISTICS,
             sensor_setting_raw=dict(
                 number_of_events=dict(count=5),
                 average_event_duration=dict(seconds=1),
                 time_elapsed_since_last_event=dict(seconds=97.0172),
                 sensing_duration=dict(seconds=1),
             )),
        id="EventStatistics"),
    pytest.param(
        b'\x59\x0e\x00\x0e\x00abcdefgh',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.DEVICE_FIRMWARE_REVISION,
             sensor_setting_property_id=PropertyID.DEVICE_FIRMWARE_REVISION,
             sensor_setting_raw=list(b'abcdefgh'),
             ),
        id="FixedString8"),
    pytest.param(
        b'\x59\x11\x00\x11\x00abcdefghabcdefghabcdefghabcdefghabcd',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.DEVICE_MANUFACTURER_NAME,
             sensor_setting_property_id=PropertyID.DEVICE_MANUFACTURER_NAME,
             sensor_setting_raw=list(b'abcdefghabcdefghabcdefghabcdefghabcd'),
             ),
        id="FixedString36"),
    pytest.param(
        b'\x59\x6a\x00\x6a\x00\xa2\x44\xff',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.TOTAL_DEVICE_ENERGY_USE,
             sensor_setting_property_id=PropertyID.TOTAL_DEVICE_ENERGY_USE,
             sensor_setting_raw=dict(
                 kilowatt_hour=0xff44a2
             )),
        id="Energy"),
    pytest.param(
        b'\x59\x2e\x00\x2e\x00\x44\xff',
        SensorOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.LIGHT_CONTROL_LIGHTNESS_ON,
             sensor_setting_property_id=PropertyID.LIGHT_CONTROL_LIGHTNESS_ON,
             sensor_setting_raw=dict(
                 perceived_lightness=0xff44
             )),
        id="PerceivedLightness"),

]


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_parse_valid(encoded, opcode, data):
    assert SensorMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_build_valid(encoded, opcode, data):
    assert SensorMessage.build(dict(opcode=opcode, params=data)) == \
        encoded


@pytest.mark.parametrize("encoded,opcode,data", valid_properties)
def test_parse_valid_property(encoded, opcode, data):
    assert SensorMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid_properties)
def test_build_valid_property(encoded, opcode, data):
    assert SensorMessage.build(dict(opcode=opcode, params=data)) == \
        encoded