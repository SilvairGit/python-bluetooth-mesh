import pytest

from bluetooth_mesh.messages.silvair.rrule_scheduler import (
    Days,
    Freqs,
    RRuleSchedulerSubMessage,
    RRuleSchedulerSubOpcode,
    RuleIDs,
    SchedulerModes,
    StatusCodes,
)

valid = [
    pytest.param(
        bytes.fromhex("080501CDAB00000001030200020500"),
        RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_ENTRY_SET,
        {
            "entry_id": 0x05,
            "slots": [{"slot_id": 0xABCD, "element": 0x00, "slot_parameter": b""}],
            "rules": [
                {"rule_id": RuleIDs.FREQ, "rule": Freqs.MINUTELY},
                {"rule_id": RuleIDs.INTERVAL, "rule": 0x02},
                {"rule_id": RuleIDs.COUNT, "rule": 0x05},
            ],
        },
    ),
    pytest.param(
        bytes.fromhex(
            "080503CDAB0002BBCCCCAB0205ABFF157288CBAB05100002BB"
            "CCCCAB0005ABFF157288CBAB000001030200020500"
        ),
        RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_ENTRY_SET,
        {
            "entry_id": 0x05,
            "slots": [
                {
                    "slot_id": 0xABCD,
                    "element": 0x00,
                    "slot_parameter": bytes.fromhex("BBCC"),
                },
                {
                    "slot_id": 0xABCC,
                    "element": 0x02,
                    "slot_parameter": bytes.fromhex("ABFF157288"),
                },
                {
                    "slot_id": 0xABCB,
                    "element": 0x05,
                    "slot_parameter": bytes.fromhex("0002BBCCCCAB0005ABFF157288CBAB00"),
                },
            ],
            "rules": [
                {"rule_id": RuleIDs.FREQ, "rule": Freqs.MINUTELY},
                {"rule_id": RuleIDs.INTERVAL, "rule": 0x02},
                {"rule_id": RuleIDs.COUNT, "rule": 0x05},
            ],
        },
    ),
    pytest.param(
        bytes.fromhex(
            "080503CDAB0002BBCCCCAB0205ABFF157288CBAB05100002BB"
            "CCCCAB0005ABFF157288CBAB00000103201002055004010005"
            "02010B0603020C100704010507FA0805041011121309080400"
            "10000200300040005000000120010A040616262A0B01020C06"
            "0A001000A000D000500050010DF8C7661BE101F8C7661BE10E"
            "03E4C7661BE1EEC7661BE1F8C7661BE10F03E4C7661BE1EEC7"
            "661BE1F8C7661BE1"
        ),
        RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_ENTRY_SET,
        {
            "entry_id": 0x05,
            "slots": [
                {
                    "slot_id": 0xABCD,
                    "element": 0x00,
                    "slot_parameter": bytes.fromhex("BBCC"),
                },
                {
                    "slot_id": 0xABCC,
                    "element": 0x02,
                    "slot_parameter": bytes.fromhex("ABFF157288"),
                },
                {
                    "slot_id": 0xABCB,
                    "element": 0x05,
                    "slot_parameter": bytes.fromhex("0002BBCCCCAB0005ABFF157288CBAB00"),
                },
            ],
            "rules": [
                {"rule_id": RuleIDs.FREQ, "rule": Freqs.MINUTELY},
                {"rule_id": RuleIDs.INTERVAL, "rule": 0x1020},
                {"rule_id": RuleIDs.COUNT, "rule": 0x5005},
                {"rule_id": RuleIDs.BYSECOND, "rule": [0x00]},
                {"rule_id": RuleIDs.BYMINUTE, "rule": [0x01, 0x0B]},
                {"rule_id": RuleIDs.BYHOUR, "rule": [0x02, 0x0C, 0x10]},
                {
                    "rule_id": RuleIDs.BYDAY,
                    "rule": [
                        Days.NEXT_MONDAY,
                        Days.NEXT_FRIDAY,
                        Days.NEXT_SUNDAY,
                        Days.PREVIOUS_SATURDAY,
                    ],
                },
                {"rule_id": RuleIDs.BYMONTHDAY, "rule": [0x04, 0x10, 0x11, 0x12, 0x13]},
                {
                    "rule_id": RuleIDs.BYYEARDAY,
                    "rule": [
                        0x0004,
                        0x0010,
                        0x0002,
                        0x0030,
                        0x0040,
                        0x0050,
                        0x0100,
                        0x0120,
                    ],
                },
                {"rule_id": RuleIDs.BYWEEKNO, "rule": [0x06, 0x16, 0x26, 0x2A]},
                {"rule_id": RuleIDs.BYMONTH, "rule": 0x0201},
                {
                    "rule_id": RuleIDs.BYSETPOS,
                    "rule": [0x000A, 0x0010, 0x00A0, 0x00D0, 0x0050, 0x0150],
                },
                {
                    "rule_id": RuleIDs.DTSTART,
                    "rule": dict(
                        second=56, minute=17, hour=22, day=25, month=11, year=2040
                    ),
                },
                {
                    "rule_id": RuleIDs.UNTIL,
                    "rule": dict(
                        second=56, minute=17, hour=22, day=25, month=11, year=2040
                    ),
                },
                {
                    "rule_id": RuleIDs.EXPLICIT_RDATE,
                    "rule": [
                        dict(
                            second=56, minute=17, hour=22, day=25, month=11, year=2020
                        ),
                        dict(
                            second=56, minute=17, hour=22, day=25, month=11, year=2030
                        ),
                        dict(
                            second=56, minute=17, hour=22, day=25, month=11, year=2040
                        ),
                    ],
                },
                {
                    "rule_id": RuleIDs.EXCLUSIONS_RDATE,
                    "rule": [
                        dict(
                            second=56, minute=17, hour=22, day=25, month=11, year=2020
                        ),
                        dict(
                            second=56, minute=17, hour=22, day=25, month=11, year=2030
                        ),
                        dict(
                            second=56, minute=17, hour=22, day=25, month=11, year=2040
                        ),
                    ],
                },
            ],
        },
    ),
]


@pytest.mark.parametrize("encoded, subopcode, payload", valid)
def test_parse_schedule_register_entry_format(encoded, subopcode, payload):
    decoded = RRuleSchedulerSubMessage.parse(encoded)
    assert decoded.subopcode == subopcode

    assert decoded.payload.entry_id == (payload["entry_id"])

    for idx, sl in enumerate(decoded.payload.scheduler_register_entry.array_of_slots):
        assert sl["slot_id"] == payload["slots"][idx]["slot_id"]
        assert sl["element"] == payload["slots"][idx]["element"]
        assert sl["slot_parameter"] == payload["slots"][idx]["slot_parameter"]

    for idx, rl in enumerate(decoded.payload.scheduler_register_entry.rules):
        assert rl["rule_id"] == payload["rules"][idx]["rule_id"]
        assert rl["rule"] == payload["rules"][idx]["rule"]


def test_scheduler_rules_list_status():
    encoded = bytes.fromhex("010102030405")
    payload = {
        RuleIDs.BYMINUTE,
        RuleIDs.BYSECOND,
        RuleIDs.INTERVAL,
        RuleIDs.UNTIL,
        RuleIDs.COUNT,
    }
    decoded = RRuleSchedulerSubMessage.parse(encoded)
    assert decoded.subopcode == RRuleSchedulerSubOpcode.RULES_LIST_STATUS
    assert decoded.payload.rule_ids == payload


def test_scheduler_max_size_status():
    encoded = bytes.fromhex("03EFCDAB89")
    decoded = RRuleSchedulerSubMessage.parse(encoded)
    assert decoded.subopcode == RRuleSchedulerSubOpcode.REGISTER_MAX_SIZE_STATUS
    assert decoded.payload.register_max_size == 0x89ABCDEF


def test_scheduler_mode_set():
    encoded = bytes.fromhex("0501")
    decoded = RRuleSchedulerSubMessage.parse(encoded)
    assert decoded.subopcode == RRuleSchedulerSubOpcode.SCHEDULER_MODE_SET
    assert decoded.payload.scheduler_mode == SchedulerModes.ENABLED


def test_scheduler_register_entry_status_no_register_entry():
    encoded = bytes.fromhex("0BFE03")
    decoded = RRuleSchedulerSubMessage.parse(encoded)
    assert decoded.subopcode == RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_ENTRY_STATUS
    assert decoded.payload.entry_id == 0xFE
    assert decoded.payload.status == StatusCodes.INVALID_RULE


def test_scheduler_register_entry_status_with_register_entry():
    encoded = bytes.fromhex("0BFE0001CDAB00020A0B000203020002050006020F17")
    decoded = RRuleSchedulerSubMessage.parse(encoded)
    assert decoded.subopcode == RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_ENTRY_STATUS
    assert decoded.payload.entry_id == 0xFE
    assert decoded.payload.status == StatusCodes.SUCCESS

    print(decoded)
    register_entry = {
        "entry_id": 0x05,
        "slots": [
            {
                "slot_id": 0xABCD,
                "element": 0x00,
                "slot_parameter": bytes.fromhex("0A0B"),
            }
        ],
        "rules": [
            {"rule_id": RuleIDs.FREQ, "rule": Freqs.HOURLY},
            {"rule_id": RuleIDs.INTERVAL, "rule": 0x02},
            {"rule_id": RuleIDs.COUNT, "rule": 0x05},
            {"rule_id": RuleIDs.BYHOUR, "rule": [15, 23]},
        ],
    }
    for idx, sl in enumerate(decoded.payload.scheduler_register_entry.array_of_slots):
        assert sl["slot_id"] == register_entry["slots"][idx]["slot_id"]
        assert sl["element"] == register_entry["slots"][idx]["element"]
        assert sl["slot_parameter"] == register_entry["slots"][idx]["slot_parameter"]

    for idx, rl in enumerate(decoded.payload.scheduler_register_entry.rules):
        assert rl["rule_id"] == register_entry["rules"][idx]["rule_id"]
        assert rl["rule"] == register_entry["rules"][idx]["rule"]


def test_scheduler_register_list_status():
    encoded = bytes.fromhex("0D01050A")
    decoded = RRuleSchedulerSubMessage.parse(encoded)

    assert decoded.subopcode == RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_LIST_STATUS
    assert decoded.payload.entry_ids == {1, 5, 10}
