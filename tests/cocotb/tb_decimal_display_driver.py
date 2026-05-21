import cocotb
from cocotb.triggers import Timer

# Active-high segment encoding for digits 0-9: [g,f,e,d,c,b,a]
SEGMENTS_ACTIVE_HIGH = {
    0: 0b0111111,
    1: 0b0000110,
    2: 0b1011011,
    3: 0b1001111,
    4: 0b1100110,
    5: 0b1101101,
    6: 0b1111101,
    7: 0b0000111,
    8: 0b1111111,
    9: 0b1101111,
}

SEGMENT_MASK = 0b1111111
ALL_OFF = SEGMENT_MASK  # active-low: all segments off = all bits high


def expected_segments(digit):
    """Return the expected active-low segment pattern for a decimal digit."""
    return (~SEGMENTS_ACTIVE_HIGH[digit]) & SEGMENT_MASK


async def drive(dut, v0, v1, v2, b0=0, b1=0, b2=0):
    dut.value0.value = v0
    dut.value1.value = v1
    dut.value2.value = v2
    dut.blank0.value = b0
    dut.blank1.value = b1
    dut.blank2.value = b2
    await Timer(1, unit="ns")


@cocotb.test()
async def test_spot_checks(dut):
    """Verify a selection of values on all three channels."""
    cocotb.log.info("Test: spot-check values on all three channels")

    cases = [
        # (value, expected_tens_digit, expected_ones_digit)
        (0,  0, 0),
        (1,  0, 1),
        (9,  0, 9),
        (10, 1, 0),
        (42, 4, 2),
        (99, 9, 9),
    ]

    for value, tens, ones in cases:
        await drive(dut, v0=value, v1=value, v2=value)

        exp_tens = expected_segments(tens)
        exp_ones = expected_segments(ones)

        for hex_tens, hex_ones, ch in [
            (dut.HEX1, dut.HEX0, 0),
            (dut.HEX3, dut.HEX2, 1),
            (dut.HEX5, dut.HEX4, 2),
        ]:
            actual_tens = int(hex_tens.value)
            actual_ones = int(hex_ones.value)
            assert actual_tens == exp_tens, (
                f"value{ch}={value}: HEX{2*ch+1} (tens) expected "
                f"0b{exp_tens:07b}, got 0b{actual_tens:07b}"
            )
            assert actual_ones == exp_ones, (
                f"value{ch}={value}: HEX{2*ch} (ones) expected "
                f"0b{exp_ones:07b}, got 0b{actual_ones:07b}"
            )


@cocotb.test()
async def test_blanking(dut):
    """Verify that asserting blank turns off both digits of that channel only."""
    cocotb.log.info("Test: blanking each channel independently")

    await drive(dut, v0=42, v1=42, v2=42, b0=1, b1=0, b2=0)
    assert int(dut.HEX0.value) == ALL_OFF, "blank0: HEX0 should be off"
    assert int(dut.HEX1.value) == ALL_OFF, "blank0: HEX1 should be off"
    assert int(dut.HEX2.value) != ALL_OFF, "blank0: HEX2 should not be off"
    assert int(dut.HEX3.value) != ALL_OFF, "blank0: HEX3 should not be off"

    await drive(dut, v0=42, v1=42, v2=42, b0=0, b1=1, b2=0)
    assert int(dut.HEX2.value) == ALL_OFF, "blank1: HEX2 should be off"
    assert int(dut.HEX3.value) == ALL_OFF, "blank1: HEX3 should be off"
    assert int(dut.HEX0.value) != ALL_OFF, "blank1: HEX0 should not be off"
    assert int(dut.HEX4.value) != ALL_OFF, "blank1: HEX4 should not be off"

    await drive(dut, v0=42, v1=42, v2=42, b0=0, b1=0, b2=1)
    assert int(dut.HEX4.value) == ALL_OFF, "blank2: HEX4 should be off"
    assert int(dut.HEX5.value) == ALL_OFF, "blank2: HEX5 should be off"
    assert int(dut.HEX2.value) != ALL_OFF, "blank2: HEX2 should not be off"
    assert int(dut.HEX3.value) != ALL_OFF, "blank2: HEX3 should not be off"


@cocotb.test()
async def test_channels_independent(dut):
    """Verify that each channel displays its own value independently."""
    cocotb.log.info("Test: channels are independent")

    await drive(dut, v0=12, v1=34, v2=56)

    assert int(dut.HEX1.value) == expected_segments(1), "HEX1 (tens of 12)"
    assert int(dut.HEX0.value) == expected_segments(2), "HEX0 (ones of 12)"
    assert int(dut.HEX3.value) == expected_segments(3), "HEX3 (tens of 34)"
    assert int(dut.HEX2.value) == expected_segments(4), "HEX2 (ones of 34)"
    assert int(dut.HEX5.value) == expected_segments(5), "HEX5 (tens of 56)"
    assert int(dut.HEX4.value) == expected_segments(6), "HEX4 (ones of 56)"
