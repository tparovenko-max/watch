import cocotb
from cocotb.triggers import Timer

# Active-high segment encoding: [g,f,e,d,c,b,a]
# A '1' means the segment is on.
EXPECTED_ACTIVE_HIGH = {
    0x0: 0b0111111,  # a,b,c,d,e,f
    0x1: 0b0000110,  # b,c
    0x2: 0b1011011,  # a,b,d,e,g
    0x3: 0b1001111,  # a,b,c,d,g
    0x4: 0b1100110,  # b,c,f,g
    0x5: 0b1101101,  # a,c,d,f,g
    0x6: 0b1111101,  # a,c,d,e,f,g
    0x7: 0b0000111,  # a,b,c
    0x8: 0b1111111,  # a,b,c,d,e,f,g
    0x9: 0b1101111,  # a,b,c,d,f,g
    0xA: 0b1110111,  # a,b,c,e,f,g
    0xB: 0b1111100,  # c,d,e,f,g
    0xC: 0b0111001,  # a,d,e,f
    0xD: 0b1011110,  # b,c,d,e,g
    0xE: 0b1111001,  # a,d,e,f,g
    0xF: 0b1110001,  # a,e,f,g
}

SEGMENT_MASK = 0b1111111  # 7 bits


@cocotb.test()
async def test_seven_segment(dut):
    ACTIVE_LOW = int(dut.ACTIVE_LOW.value)
    cocotb.log.info(f"Testing seven_segment with ACTIVE_LOW={ACTIVE_LOW}")

    # --- blank input turns off all segments ---
    cocotb.log.info("Test 1: Blank input disables all segments")
    dut.blank.value = 1
    dut.digit.value = 0
    await Timer(1, unit="ns")
    actual = int(dut.segments.value)
    expected = SEGMENT_MASK if ACTIVE_LOW else 0
    assert actual == expected, (
        f"blank=1: expected segments=0b{expected:07b}, got 0b{actual:07b}"
    )

    # --- all 16 hex digits ---
    cocotb.log.info("Test 2: All 16 hex digits")
    dut.blank.value = 0
    for digit, active_high in EXPECTED_ACTIVE_HIGH.items():
        dut.digit.value = digit
        await Timer(1, unit="ns")
        actual = int(dut.segments.value)
        expected = (~active_high & SEGMENT_MASK) if ACTIVE_LOW else active_high
        assert actual == expected, (
            f"digit=0x{digit:X}: expected segments=0b{expected:07b}, "
            f"got 0b{actual:07b} (ACTIVE_LOW={ACTIVE_LOW})"
        )

    # --- blank overrides all digits ---
    cocotb.log.info("Test 3: Blank overrides all digits")
    expected = SEGMENT_MASK if ACTIVE_LOW else 0
    dut.blank.value = 1
    for digit in EXPECTED_ACTIVE_HIGH:
        dut.digit.value = digit
        await Timer(1, unit="ns")
        actual = int(dut.segments.value)
        assert actual == expected, (
            f"blank=1 with digit=0x{digit:X}: expected segments=0b{expected:07b}, "
            f"got 0b{actual:07b}"
        )
