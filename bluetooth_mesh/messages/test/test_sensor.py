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
import sys
from datetime import date

import pytest

from bluetooth_mesh.messages.properties import PropertyID
from bluetooth_mesh.messages.sensor import (
    SensorMessage,
    SensorOpcode,
    SensorSampling,
    SensorSettingAccess,
    SensorSetupMessage,
    SensorSetupOpcode,
)

valid = [
    # fmt: off
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
        b'\x51\x0c\x00\x00\x00\x00\x04\x0b\x0c',
        SensorOpcode.SENSOR_DESCRIPTOR_STATUS,
        [dict(sensor_property_id=PropertyID.DEVICE_DATE_OF_MANUFACTURE,
              sensor_positive_tolerance=0x00,
              sensor_negative_tolerance=0x00,
              sensor_sampling_funcion=SensorSampling.MAXIMUM,
              sensor_measurement_period=0x0b,
              sensor_update_interval=0x0c)],
        id="SENSOR_DESCRIPTOR_STATUS"),
    pytest.param(
        b'\x51\x19\x00',
        SensorOpcode.SENSOR_DESCRIPTOR_STATUS,
        [dict(sensor_property_id=PropertyID.DEVICE_SERIAL_NUMBER)],
        id="SENSOR_DESCRIPTOR_STATUS_not_existing"),
    pytest.param(
        b'\x51\x0c\x00\x00\x00\x00\x02\x0b\x0c\x1f\x00\xef\xcd\xab\x07\x1b\x1c',
        SensorOpcode.SENSOR_DESCRIPTOR_STATUS,
        [dict(sensor_property_id=PropertyID.DEVICE_DATE_OF_MANUFACTURE,
              sensor_positive_tolerance=0x00,
              sensor_negative_tolerance=0x00,
              sensor_sampling_funcion=SensorSampling.ARITHMETIC_MEAN,
              sensor_measurement_period=0x0b,
              sensor_update_interval=0x0c),
         dict(sensor_property_id=PropertyID.INITIAL_LUMINOUS_FLUX,
              sensor_positive_tolerance=0xabc,
              sensor_negative_tolerance=0xdef,
              sensor_sampling_funcion=SensorSampling.COUNT,
              sensor_measurement_period=0x1b,
              sensor_update_interval=0x1c)],
        id="SENSOR_DESCRIPTOR_STATUS_multiple"),

    pytest.param(
        b'\x52\xe2\x0a\xc8\x00',
        SensorOpcode.SENSOR_STATUS,
        [dict(sensor_setting_property_id=PropertyID.PRESENT_INPUT_CURRENT,
              length=2,
              format=0,
              present_input_current=dict(current=2.0))],
        id="SENSOR_STATUS_PRESENT_INPUT_CURRENT"),
    pytest.param(
        b'\x52\x22\x0b\x20\x03',
        SensorOpcode.SENSOR_STATUS,
        [dict(sensor_setting_property_id=PropertyID.PRESENT_INPUT_VOLTAGE,
              length=2,
              format=0,
              present_input_voltage=dict(voltage=12.5))
        ],
        id="SENSOR_STATUS_PRESENT_INPUT_VOLTAGE"),
    pytest.param(
        b'\x52\x44\x0d\xa2\x44\xff',
        SensorOpcode.SENSOR_STATUS,
        [dict(sensor_setting_property_id=PropertyID.TOTAL_DEVICE_ENERGY_USE,
              length=3,
              format=0,
              total_device_energy_use=dict(
                  energy=0xff44a2))
        ],
        id="SENSOR_STATUS_TOTAL_DEVICE_ENERGY_USE"),
    pytest.param(
        b'\x52\x09\x90\x40\xa2\x44\xff\x00\x00',
        SensorOpcode.SENSOR_STATUS,
        [dict(sensor_setting_property_id=0x4090,
              length=5,
              format=1,
              sensor_setting_raw=list(b'\xa2\x44\xff\x00\x00'))
        ],
        id="SENSOR_STATUS_VENDOR_PROPERTY"),
    pytest.param(
        b'\x52\x44\x0d\xa2\x44\xff\x22\x0b\x20\x03',
        SensorOpcode.SENSOR_STATUS,
        [dict(sensor_setting_property_id=PropertyID.TOTAL_DEVICE_ENERGY_USE,
              length=3,
              format=0,
              total_device_energy_use=dict(energy=0xff44a2)),
         dict(sensor_setting_property_id=PropertyID.PRESENT_INPUT_VOLTAGE,
              length=2,
              format=0,
              present_input_voltage=dict(voltage=12.5))
         ],
        id="SENSOR_STATUS_2_SHORT_PROP"),
    # fmt: on
]

valid_setup = [
    # fmt: off
    pytest.param(
        b'\x58\x30\x00\x01\x00\x04\x00\x09\x00',
        SensorSetupOpcode.SENSOR_SETTINGS_STATUS,
        dict(sensor_property_id=PropertyID.LIGHT_CONTROL_LIGHTNESS_STANDBY,
             sensor_setting_property_ids=[PropertyID.AVERAGE_AMBIENT_TEMPERATURE_IN_A_PERIOD_OF_DAY,
                                          PropertyID.AVERAGE_OUTPUT_CURRENT,
                                          PropertyID.COLOR_RENDERING_INDEX_RA]),
        id="SENSOR_SETTINGS_STATUS"),
    pytest.param(
        b'\x58\x30\x00',
        SensorSetupOpcode.SENSOR_SETTINGS_STATUS,
        dict(sensor_property_id=PropertyID.LIGHT_CONTROL_LIGHTNESS_STANDBY,
             sensor_setting_property_ids=[]),
        id="SENSOR_SETTING_STATUS_empty"),
    pytest.param(
        b'\x59\x57\x00\x57\x00\xc8\x00',
        SensorSetupOpcode.SENSOR_SETTING_SET,
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             present_input_current=dict(
                 current=2.0)),
        id="SENSOR_SETTING_SET"),
    pytest.param(
        b'\x5b\x57\x00\x57\x00\x01\xc8\x00',
        SensorSetupOpcode.SENSOR_SETTING_STATUS,
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_access=SensorSettingAccess.READ_ONLY,
             present_input_current=dict(
                 current=2.0)),
        id="SENSOR_SETTING_STATUS"),
    pytest.param(
        b'\x5b\x57\x00\x02\x00\x01\xc8\x00\x39',
        SensorSetupOpcode.SENSOR_SETTING_STATUS,
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_property_id=PropertyID.AVERAGE_INPUT_CURRENT,
             sensor_setting_access=SensorSettingAccess.READ_ONLY,
             average_input_current=dict(
                 electric_current_value=2.0,
                 sensing_duration=dict(seconds=0.5132))),
        id="SENSOR_SETTING_STATUS"),
    # fmt: on
]

valid_properties = [
    # fmt: off
    pytest.param(
        b'\x59\x57\x00\x57\x00\xc8\x00',
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             present_input_current=dict(
                 current=2.0)),
        id="ElectricCurrent"),
    pytest.param(
        b'\x59\x57\x00\x02\x00\xc8\x00\x39',
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_property_id=PropertyID.AVERAGE_INPUT_CURRENT,
             average_input_current=dict(
                 electric_current_value=2.0,
                 sensing_duration=dict(seconds=0.5132))),
        id="AverageCurrent"),
    pytest.param(
        b'\x59\x05\x00\x05\x00\x20\x03\x54',
        dict(sensor_property_id=PropertyID.AVERAGE_OUTPUT_VOLTAGE,
             sensor_setting_property_id=PropertyID.AVERAGE_OUTPUT_VOLTAGE,
             average_output_voltage=dict(
                 voltage_value=12.5,
                 sensing_duration=dict(seconds=6.7275))),
        id="AverageVoltage"),
    pytest.param(
        b'\x59\x57\x00\x02\x00\xc8\x00\x00',
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_CURRENT,
             sensor_setting_property_id=PropertyID.AVERAGE_INPUT_CURRENT,
             average_input_current=dict(
                 electric_current_value=2.0,
                 sensing_duration=dict(seconds=0))),
        id="AverageCurrent_with_0"),
    pytest.param(
        b'\x59\x59\x00\x59\x00\x00\x03',
        dict(sensor_property_id=PropertyID.PRESENT_INPUT_VOLTAGE,
             sensor_setting_property_id=PropertyID.PRESENT_INPUT_VOLTAGE,
             present_input_voltage=dict(
                 voltage=12)),
        id="Voltage"),
    pytest.param(
        b'\x59\x42\x00\x4d\x00\x01',
        dict(sensor_property_id=PropertyID.MOTION_SENSED,
             sensor_setting_property_id=PropertyID.PRESENCE_DETECTED,
             presence_detected=dict(
                 presence_detected=True)),
        id="Presence"),
    pytest.param(
        b'\x59\x42\x00\x42\x00\x50',
        dict(sensor_property_id=PropertyID.MOTION_SENSED,
             sensor_setting_property_id=PropertyID.MOTION_SENSED,
             motion_sensed=dict(
                 percentage=40)),
        id="Percentage8"),
    pytest.param(
        b'\x59\x0a\x00\x36\x00\xb8\x0b\x00',
        dict(sensor_property_id=PropertyID.DEVICE_APPEARANCE,
             sensor_setting_property_id=PropertyID.LIGHT_CONTROL_TIME_FADE,
             light_control_time_fade=dict(
                 seconds=3)),
        id="TimeMiliseconds24"),
    pytest.param(
        b'\x59\x6d\x00\x6d\x00\x0a\x00\x00',
        dict(sensor_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_TIME,
             sensor_setting_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_TIME,
             total_device_power_on_time=dict(
                 hours=10)),
        id="TimeHour24"),
    pytest.param(
        b'\x59\x6d\x00\x6d\x00\xff\xff\xff',
        dict(sensor_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_TIME,
             sensor_setting_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_TIME,
             total_device_power_on_time=dict(
                 hours=float(sys.float_info.max))),
        id="TimeHour24_unknown"),
    pytest.param(
        b'\x59\x55\x00\x55\x00\x1a\x27\x00',
        dict(sensor_property_id=PropertyID.PRESENT_ILLUMINANCE,
             sensor_setting_property_id=PropertyID.PRESENT_ILLUMINANCE,
             present_illuminance=dict(
                 illuminance=100.1)),
        id="Illuminance"),
    pytest.param(
        b'\x59\x4c\x00\x4c\x00\x1b\x1a',
        dict(sensor_property_id=PropertyID.PEOPLE_COUNT,
             sensor_setting_property_id=PropertyID.PEOPLE_COUNT,
             people_count=dict(
                 count=0x1a1b)),
        id="Count16"),
    pytest.param(
        b'\x59\x6c\x00\x6c\x00\xff\x1b\x1a',
        dict(sensor_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_CYCLES,
             sensor_setting_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_CYCLES,
             total_device_power_on_cycles=dict(
                 count=0x1a1bff)),
        id="Count24"),
    pytest.param(
        b'\x59\x6c\x00\x6c\x00\xff\xff\xff',
        dict(sensor_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_CYCLES,
             sensor_setting_property_id=PropertyID.TOTAL_DEVICE_POWER_ON_CYCLES,
             total_device_power_on_cycles=dict(
                 count=float(sys.float_info.max))),
        id="Count24_unknown"),
    pytest.param(
        b'\x59\x68\x00\x68\x00\x05\x00',
        dict(sensor_property_id=PropertyID.TIME_SINCE_MOTION_SENSED,
             sensor_setting_property_id=PropertyID.TIME_SINCE_MOTION_SENSED,
             time_since_motion_sensed=dict(
                 seconds=5)),
        id="TimeSecond16"),
    pytest.param(
        b'\x59\x67\x00\x67\x00\x05\x00\x01\x00\x70\x40',
        dict(sensor_property_id=PropertyID.SHORT_CIRCUIT_EVENT_STATISTICS,
             sensor_setting_property_id=PropertyID.SHORT_CIRCUIT_EVENT_STATISTICS,
             short_circuit_event_statistics=dict(
                 number_of_events=dict(count=5),
                 average_event_duration=dict(seconds=1),
                 time_elapsed_since_last_event=dict(seconds=97.0172),
                 sensing_duration=dict(seconds=1),
             )),
        id="EventStatistics"),
    pytest.param(
        b'\x59\x0e\x00\x0e\x00abcdefgh',
        dict(sensor_property_id=PropertyID.DEVICE_FIRMWARE_REVISION,
             sensor_setting_property_id=PropertyID.DEVICE_FIRMWARE_REVISION,
             device_firmware_revision="abcdefgh",
             ),
        id="FixedString8"),
    pytest.param(
        b'\x59\x0e\x00\x0e\x00abcdef\x00\x00',
        dict(sensor_property_id=PropertyID.DEVICE_FIRMWARE_REVISION,
             sensor_setting_property_id=PropertyID.DEVICE_FIRMWARE_REVISION,
             device_firmware_revision='abcdef',
             ),
        id="FixedString8_padded"),
    pytest.param(
        b'\x59\x11\x00\x11\x00abcdefghabcdefghabcdefghabcdefghabcd',
        dict(sensor_property_id=PropertyID.DEVICE_MANUFACTURER_NAME,
             sensor_setting_property_id=PropertyID.DEVICE_MANUFACTURER_NAME,
             device_manufacturer_name='abcdefghabcdefghabcdefghabcdefghabcd',
             ),
        id="FixedString36"),
    pytest.param(
        b'\x59\x6a\x00\x6a\x00\xa2\x44\xff',
        dict(sensor_property_id=PropertyID.TOTAL_DEVICE_ENERGY_USE,
             sensor_setting_property_id=PropertyID.TOTAL_DEVICE_ENERGY_USE,
             total_device_energy_use=dict(
                 energy=0xff44a2
             )),
        id="Energy"),
    pytest.param(
        b'\x59\x2e\x00\x2e\x00\x44\xff',
        dict(sensor_property_id=PropertyID.LIGHT_CONTROL_LIGHTNESS_ON,
             sensor_setting_property_id=PropertyID.LIGHT_CONTROL_LIGHTNESS_ON,
             light_control_lightness_on=dict(
                 perceived_lightness=0xff44
             )),
        id="PerceivedLightness"),
    pytest.param(
        b'\x59\x32\x00\x32\x00\x44\xff\x00\x00',
        dict(sensor_property_id=PropertyID.LIGHT_CONTROL_REGULATOR_KID,
             sensor_setting_property_id=PropertyID.LIGHT_CONTROL_REGULATOR_KID,
             light_control_regulator_kid=dict(
                 coefficient=0x0000ff44
             )),
        id="Coefficient"),
    pytest.param(
        b'\x59\x52\x00\x52\x00\xa0\x86\x01',
        dict(sensor_property_id=PropertyID.PRESENT_DEVICE_INPUT_POWER,
             sensor_setting_property_id=PropertyID.PRESENT_DEVICE_INPUT_POWER,
             present_device_input_power=dict(
                 power=10000
             )),
        id="Power"),
    pytest.param(
        b'\x59\x16\x00\x16\x00\xe8\x03\x00\xd0\x07\x00\x0f\x27\x00',
        dict(sensor_property_id=PropertyID.DEVICE_POWER_RANGE_SPECIFICATION,
             sensor_setting_property_id=PropertyID.DEVICE_POWER_RANGE_SPECIFICATION,
             device_power_range_specification=dict(
                 minimum_power_value=100,
                 typical_power_value=200,
                 maximum_power_value=999.9,
             )),
        id="PowerSpecification"),
    pytest.param(
        b'\x59\x4f\x00\x4f\x00\x1f',
        dict(sensor_property_id=PropertyID.PRESENT_AMBIENT_TEMPERATURE,
             sensor_setting_property_id=PropertyID.PRESENT_AMBIENT_TEMPERATURE,
             present_ambient_temperature=dict(
                 temperature=15.5,
             )),
        id="Temperature8_positive"),
    pytest.param(
        b'\x59\x4f\x00\x4f\x00\xe1',
        dict(sensor_property_id=PropertyID.PRESENT_AMBIENT_TEMPERATURE,
             sensor_setting_property_id=PropertyID.PRESENT_AMBIENT_TEMPERATURE,
             present_ambient_temperature=dict(
                 temperature=-15.5,
             )),
        id="Temperature8_negative"),
    pytest.param(
        b'\x59\x54\x00\x54\x00\xe6\x20',
        dict(sensor_property_id=PropertyID.PRESENT_DEVICE_OPERATING_TEMPERATURE,
             sensor_setting_property_id=PropertyID.PRESENT_DEVICE_OPERATING_TEMPERATURE,
             present_device_operating_temperature=dict(
                 temperature=84.22,
             )),
        id="Temperature_positive"),
    pytest.param(
        b'\x59\x45\x00\x45\x00\x31\x02\xdc\x6e\x71',
        dict(sensor_property_id=PropertyID.OUTDOOR_STATISTICAL_VALUES,
             sensor_setting_property_id=PropertyID.OUTDOOR_STATISTICAL_VALUES,
             outdoor_statistical_values=dict(
                 average_temperature=24.5,
                 standard_deviation_temperature=1,
                 minimum_temperature=-18,
                 maximum_temperature=55,
                 sensing_duration=dict(seconds=106.719),
             )),
        id="Temperature8Statistics"),
    pytest.param(
        b'\x59\x14\x00\x14\x00\x92\x09\x64\x00\xf8\xf8\x20\x4e\x71',
        dict(sensor_property_id=PropertyID.DEVICE_OPERATING_TEMPERATURE_STATISTICAL_VALUES,
             sensor_setting_property_id=PropertyID.DEVICE_OPERATING_TEMPERATURE_STATISTICAL_VALUES,
             device_operating_temperature_statistical_values=dict(
                 average_temperature=24.5,
                 standard_deviation_temperature=1,
                 minimum_temperature=-18,
                 maximum_temperature=200,
                 sensing_duration=dict(seconds=106.719),
             )),
        id="TemperatureStatistics"),
    pytest.param(
        b'\x59\x13\x00\x13\x00\xdc\x6e',
        dict(sensor_property_id=PropertyID.DEVICE_OPERATING_TEMPERATURE_RANGE_SPECIFICATION,
             sensor_setting_property_id=PropertyID.DEVICE_OPERATING_TEMPERATURE_RANGE_SPECIFICATION,
             device_operating_temperature_range_specification=dict(
                 minimum_temperature=-18,
                 maximum_temperature=55,
             )),
        id="TemperatureRange"),
    pytest.param(
        b'\x59\x01\x00\x01\x00\x18\x6d\xa2',
        dict(sensor_property_id=PropertyID.AVERAGE_AMBIENT_TEMPERATURE_IN_A_PERIOD_OF_DAY,
             sensor_setting_property_id=PropertyID.AVERAGE_AMBIENT_TEMPERATURE_IN_A_PERIOD_OF_DAY,
             average_ambient_temperature_in_a_period_of_day=dict(
                 temperature=12,
                 start_time=dict(hour=10.9),
                 end_time=dict(hour=16.2),
             )),
        id="Temperature8InAPeriodOfDay"),
    pytest.param(
        b'\x59\x60\x00\x60\x00\xa2\x44\xff\x6d\xa2',
        dict(sensor_property_id=PropertyID.RELATIVE_DEVICE_ENERGY_USE_IN_A_PERIOD_OF_DAY,
             sensor_setting_property_id=PropertyID.RELATIVE_DEVICE_ENERGY_USE_IN_A_PERIOD_OF_DAY,
             relative_device_energy_use_in_a_period_of_day=dict(
                 energy_value=0xff44a2,
                 start_time=dict(hour=10.9),
                 end_time=dict(hour=16.2),
             )),
        id="EnergyInAPeriodOfDay"),
    pytest.param(
        b'\x59\x2a\x00\x2a\x00\x69\x01\x40\x00\x00\x00\xf0\xff\x54',
        dict(sensor_property_id=PropertyID.INPUT_VOLTAGE_STATISTICS,
             sensor_setting_property_id=PropertyID.INPUT_VOLTAGE_STATISTICS,
             input_voltage_statistics=dict(
                 average_voltage_value=5.640625,
                 standard_deviation_voltage_value=1,
                 minimum_voltage_value=0,
                 maximum_voltage_value=1023.75,
                 sensing_duration=dict(seconds=6.7275),
             )),
        id="VoltageStatistics"),
    pytest.param(
        b'\x59\x49\x00\x49\x00\x00\x00\x00\x06\xf0\xff',
        dict(sensor_property_id=PropertyID.OUTPUT_VOLTAGE_RANGE,
             sensor_setting_property_id=PropertyID.OUTPUT_VOLTAGE_RANGE,
             output_voltage_range=dict(
                 minimum_voltage_value=0,
                 typical_voltage_value=24,
                 maximum_voltage_value=1023.75,
             )),
        id="VoltageRange"),
    pytest.param(
        b'\x59\x47\x00\x47\x00\x97\x09\x64\x00\x00\x00\x7d\x15\x71',
        dict(sensor_property_id=PropertyID.OUTPUT_CURRENT_STATISTICS,
             sensor_setting_property_id=PropertyID.OUTPUT_CURRENT_STATISTICS,
             output_current_statistics=dict(
                 average_electric_current_value=24.55,
                 standard_deviation_electric_current_value=1,
                 minimum_electric_current_value=0,
                 maximum_electric_current_value=55.01,
                 sensing_duration=dict(seconds=106.719),
             )),
        id="ElectricCurrentStatistics"),
    pytest.param(
        b'\x59\x46\x00\x46\x00\x00\x00\x7d\x15',
        dict(sensor_property_id=PropertyID.OUTPUT_CURRENT_RANGE,
             sensor_setting_property_id=PropertyID.OUTPUT_CURRENT_RANGE,
             output_current_range=dict(
                 minimum_electric_current_value=0,
                 maximum_electric_current_value=55.01,
             )),
        id="ElectricCurrentRange"),
    pytest.param(
        b'\x59\x21\x00\x21\x00\x00\x00\x01\x00\x7d\x15',
        dict(sensor_property_id=PropertyID.INPUT_CURRENT_RANGE_SPECIFICATION,
             sensor_setting_property_id=PropertyID.INPUT_CURRENT_RANGE_SPECIFICATION,
                     input_current_range_specification=dict(
                 minimum_electric_current_value=0,
                 typical_electric_current_value=0.01,
                 maximum_electric_current_value=55.01,
             )),
        id="ElectricCurrentSpecification"),
    pytest.param(
        b'\x59\x70\x00\x70\x00\x02\x00\x00',
        dict(sensor_property_id=PropertyID.TOTAL_LUMINOUS_ENERGY,
             sensor_setting_property_id=PropertyID.TOTAL_LUMINOUS_ENERGY,
             total_luminous_energy=dict(
                 luminous_energy=2000,
             )),
        id="LuminousEnergy"),
    pytest.param(
        b'\x59\x06\x00\x06\x00\x00\x20',
        dict(sensor_property_id=PropertyID.CENTER_BEAM_INTENSITY_AT_FULL_POWER,
             sensor_setting_property_id=PropertyID.CENTER_BEAM_INTENSITY_AT_FULL_POWER,
             center_beam_intensity_at_full_power=dict(
                 luminous_intensity=0x2000,
             )),
        id="LuminousIntensity"),
    pytest.param(
        b'\x59\x40\x00\x40\x00\x02\x00\x00',
        dict(sensor_property_id=PropertyID.LUMINOUS_EXPOSURE,
             sensor_setting_property_id=PropertyID.LUMINOUS_EXPOSURE,
             luminous_exposure=dict(
                 luminous_exposure=2000,
             )),
        id="LuminousExposure"),
    pytest.param(
        b'\x59\x1f\x00\x1f\x00\xd0\x07',
        dict(sensor_property_id=PropertyID.INITIAL_LUMINOUS_FLUX,
             sensor_setting_property_id=PropertyID.INITIAL_LUMINOUS_FLUX,
             initial_luminous_flux=dict(
                 luminous_flux=2000,
             )),
        id="LuminousFlux"),
    pytest.param(
        b'\x59\x41\x00\x41\x00\xe8\x03\xd0\x07',
        dict(sensor_property_id=PropertyID.LUMINOUS_FLUX_RANGE,
             sensor_setting_property_id=PropertyID.LUMINOUS_FLUX_RANGE,
             luminous_flux_range=dict(
                 minimum_luminous_flux=1000,
                 maximum_luminous_flux=2000,
             )),
        id="LuminousFluxRange"),
    pytest.param(
        b'\x59\x3e\x00\x3e\x00\xd4\x07',
        dict(sensor_property_id=PropertyID.LUMINOUS_EFFICACY,
             sensor_setting_property_id=PropertyID.LUMINOUS_EFFICACY,
             luminous_efficacy=dict(
                 luminous_efficacy=200.4,
             )),
        id="LuminousEfficacy"),
    pytest.param(
        b'\x59\x0f\x00\x0f\x00\xff\xee\xdd\xcc\xbb\xaa',
        dict(sensor_property_id=PropertyID.DEVICE_GLOBAL_TRADE_ITEM_NUMBER,
             sensor_setting_property_id=PropertyID.DEVICE_GLOBAL_TRADE_ITEM_NUMBER,
             device_global_trade_item_number=dict(
                 global_trade_item_number=0xaabbccddeeff
             )),
        id="GlobalTradeItemNumber"),
    pytest.param(
        b'\x59\x07\x00\x07\x00\x64',
        dict(sensor_property_id=PropertyID.CHROMATICITY_TOLERANCE,
             sensor_setting_property_id=PropertyID.CHROMATICITY_TOLERANCE,
             chromaticity_tolerance=dict(
                 chromaticity_tolerance=0.01,
             )),
        id="ChromaticityTolerance"),
    pytest.param(
        b'\x59\x5e\x00\x5e\x00\x92\x27',
        dict(sensor_property_id=PropertyID.PRESENT_PLANCKIAN_DISTANCE,
             sensor_setting_property_id=PropertyID.PRESENT_PLANCKIAN_DISTANCE,
             present_planckian_distance=dict(
                 distance_from_planckian=0.1013,
             )),
        id="ChromaticDistanceFromPlanckian"),
    pytest.param(
        b'\x59\x51\x00\x51\x00\xb8\x0b',
        dict(sensor_property_id=PropertyID.PRESENT_CORRELATED_COLOR_TEMPERATURE,
             sensor_setting_property_id=PropertyID.PRESENT_CORRELATED_COLOR_TEMPERATURE,
             present_correlated_color_temperature=dict(
                 correlated_color_temperature=3000,
             )),
        id="CorrelatedColorTemperature"),
    pytest.param(
        b'\x59\x0a\x00\x0a\x00\x04\xf0',
        dict(sensor_property_id=PropertyID.DEVICE_APPEARANCE,
             sensor_setting_property_id=PropertyID.DEVICE_APPEARANCE,
             device_appearance=dict(
                 category=960,
                 sub_category=4
             )),
        id="Appearance"),
    pytest.param(
        b'\x59\x0b\x00\x0b\x00\x2a\x00',
        dict(sensor_property_id=PropertyID.DEVICE_COUNTRY_OF_ORIGIN,
             sensor_setting_property_id=PropertyID.DEVICE_COUNTRY_OF_ORIGIN,
             device_country_of_origin=dict(
                 country_code=42,
             )),
        id="CountryCode"),
    pytest.param(
        b'\x59\x0c\x00\x0c\x00\xde\x46\x00',
        dict(sensor_property_id=PropertyID.DEVICE_DATE_OF_MANUFACTURE,
             sensor_setting_property_id=PropertyID.DEVICE_DATE_OF_MANUFACTURE,
             device_date_of_manufacture=dict(
                 date=date(2019, 9, 3),
             )),
        id="DateUTC"),
    pytest.param(
        b'\x59\x50\x00\x50\x00\xee\x00\xcd\xab',
        dict(sensor_property_id=PropertyID.PRESENT_CIE1931_CHROMATICITY_COORDINATES,
             sensor_setting_property_id=PropertyID.PRESENT_CIE1931_CHROMATICITY_COORDINATES,
             present_cie1931_chromaticity_coordinates=dict(
                 chromaticity_x_coordinate=0xee/0xffff,
                 chromaticity_y_coordinate=0xabcd/0xffff,
             )),
        id="ChromaticityCoordinates"),
    pytest.param(
        b'\x59\x08\x00\x08\x00\x64',
        dict(sensor_property_id=PropertyID.COLOR_RENDERING_INDEX_R9,
             sensor_setting_property_id=PropertyID.COLOR_RENDERING_INDEX_R9,
             color_rendering_index_r9=dict(
                 color_rendering_index=100,
             )),
        id="ColorRenderingIndex_positive"),
    pytest.param(
        b'\x59\x08\x00\x08\x00\x9c',
        dict(sensor_property_id=PropertyID.COLOR_RENDERING_INDEX_R9,
             sensor_setting_property_id=PropertyID.COLOR_RENDERING_INDEX_R9,
             color_rendering_index_r9=dict(
                 color_rendering_index=-100,
             )),
        id="ColorRenderingIndex_negative"),
    pytest.param(
        b'\x59\x61\x00\x61\x00\x88\xaa\x00\xbb\xbb',
        dict(sensor_property_id=PropertyID.RELATIVE_DEVICE_RUNTIME_IN_A_GENERIC_LEVEL_RANGE,
             sensor_setting_property_id=PropertyID.RELATIVE_DEVICE_RUNTIME_IN_A_GENERIC_LEVEL_RANGE,
             relative_device_runtime_in_a_generic_level_range=dict(
                 relative_value=0x44,
                 minimum_generic_level=0xaa,
                 maximum_generic_level=0xbbbb,
             )),
        id="RelativeRuntimeInAGenericLevelRange"),
    pytest.param(
        b'\x59\x62\x00\x62\x00\x88\x1a\x27\x00\x1a\x27\x00',
        dict(sensor_property_id=PropertyID.RELATIVE_EXPOSURE_TIME_IN_AN_ILLUMINANCE_RANGE,
             sensor_setting_property_id=PropertyID.RELATIVE_EXPOSURE_TIME_IN_AN_ILLUMINANCE_RANGE,
             relative_exposure_time_in_an_illuminance_range=dict(
                 relative_value=0x44,
                 minimum_illuminance=100.1,
                 maximum_illuminance=100.1,
             )),
        id="RelativeValueInAnIlluminanceRange"),
    pytest.param(
        b'\x59\x64\x00\x64\x00\x88\xff\xff\xe6\x20',
        dict(sensor_property_id=PropertyID.RELATIVE_RUNTIME_IN_A_DEVICE_OPERATING_TEMPERATURE_RANGE,
             sensor_setting_property_id=PropertyID.RELATIVE_RUNTIME_IN_A_DEVICE_OPERATING_TEMPERATURE_RANGE,
             relative_runtime_in_a_device_operating_temperature_range=dict(
                 relative_value=0x44,
                 minimum_temperature=-0.01,
                 maximum_temperature=84.22,
             )),
        id="RelativeValueInATemperatureRange"),
    pytest.param(
        b'\x59\x65\x00\x65\x00\x88\x00\x00\xcd\xab',
        dict(sensor_property_id=PropertyID.RELATIVE_RUNTIME_IN_AN_INPUT_CURRENT_RANGE,
             sensor_setting_property_id=PropertyID.RELATIVE_RUNTIME_IN_AN_INPUT_CURRENT_RANGE,
             relative_runtime_in_an_input_current_range=dict(
                 relative_value=0x44,
                 minimum_current=0,
                 maximum_current=439.81,
             )),
        id="RelativeValueInACurrentRange"),
    pytest.param(
        b'\x59\x66\x00\x66\x00\x88\x20\x03\x20\x03',
        dict(sensor_property_id=PropertyID.RELATIVE_RUNTIME_IN_AN_INPUT_VOLTAGE_RANGE,
             sensor_setting_property_id=PropertyID.RELATIVE_RUNTIME_IN_AN_INPUT_VOLTAGE_RANGE,
             relative_runtime_in_an_input_voltage_range=dict(
                 relative_value=0x44,
                 minimum_voltage=12.5,
                 maximum_voltage=12.5
             )),
        id="RelativeValueInAVoltageRange"),
    # fmt: on
]


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_parse_valid(encoded, opcode, data):
    assert SensorMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_build_valid(encoded, opcode, data):
    assert SensorMessage.build(dict(opcode=opcode, params=data)) == encoded


@pytest.mark.parametrize("encoded,opcode,data", valid_setup)
def test_parse_valid_setup(encoded, opcode, data):
    assert SensorSetupMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid_setup)
def test_build_valid_setup(encoded, opcode, data):
    assert SensorSetupMessage.build(dict(opcode=opcode, params=data)) == encoded


@pytest.mark.parametrize("encoded,data", valid_properties)
def test_parse_valid_property(encoded, data):
    assert SensorSetupMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,data", valid_properties)
def test_build_valid_property(encoded, data):
    assert (
        SensorSetupMessage.build(
            dict(opcode=SensorSetupOpcode.SENSOR_SETTING_SET, params=data)
        )
        == encoded
    )


def test_parse_sensor_setting_raw():
    sensor_status = SensorMessage.parse(b"\x52\xe2\x0a\xc8\x00").params[0]
    assert sensor_status.sensor_setting_raw == sensor_status.present_input_current


def test_build_sensor_setting_raw():
    encoded = SensorMessage.build(
        dict(
            opcode=SensorOpcode.SENSOR_STATUS,
            params=[
                dict(
                    sensor_setting_property_id=PropertyID.PRESENT_INPUT_CURRENT,
                    length=2,
                    format=0,
                    sensor_setting_raw=dict(current=2.0),
                )
            ],
        )
    )
    assert encoded == b"\x52\xe2\x0a\xc8\x00"
