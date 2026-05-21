import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

# Segment encoding (active-low, [g,f,e,d,c,b,a])
_ACTIVE_HIGH = {
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
_SEG_MASK = 0b1111111
ALL_OFF = _SEG_MASK  # active-low: all segments off = all bits high


def seg(digit):
    """Expected active-low segment value for a decimal digit 0-9."""
    return (~_ACTIVE_HIGH[digit]) & _SEG_MASK


async def step(dut):
    """Advance one clock cycle and wait for registered outputs to settle."""
    await RisingEdge(dut.CLOCK_50)
    await Timer(1, unit="ns")


async def set_keys(dut, pressed_mask):
    """Drive KEY signals and wait 2 cycles for the synchroniser to settle.

    pressed_mask: bitmask of which keys are pressed (1 = pressed).
    """
    dut.KEY.value = (~pressed_mask) & 0xF  # active-low
    await step(dut)
    await step(dut)


@cocotb.test()
async def test_sw_led_clk_mux(dut):
    """LEDR shows SW when clk=1, ~SW when clk=0 (user_top)."""
    dut.KEY.value = 0xF  # all released
    for sw_val in [0b00_0000_0000, 0b11_1111_1111, 0b10_1010_1010, 0b01_0101_0101]:
        dut.SW.value = sw_val
        dut.CLOCK_50.value = 1
        await Timer(1, unit="ns")
        assert int(dut.LEDR.value) == sw_val, (
            f"LEDR should equal SW when clk=1; SW={sw_val:#012b}, got LEDR={int(dut.LEDR.value):#012b}"
        )
        dut.CLOCK_50.value = 0
        await Timer(1, unit="ns")
        assert int(dut.LEDR.value) == (~sw_val & 0x3FF), (
            f"LEDR should equal ~SW when clk=0; SW={sw_val:#012b}, got LEDR={int(dut.LEDR.value):#012b}"
        )


@cocotb.test()
async def test_display_values_button3_low(dut):
    """With button[3]=0 (KEY[3] released), verify all six HEX outputs.

    user_top drives: seconds=45, minutes=23, hours=7.
    """
    cocotb.start_soon(Clock(dut.CLOCK_50, 20, unit="ns").start())
    dut.SW.value = 0
    await set_keys(dut, pressed_mask=0b0000)

    cocotb.log.info(
        "Test: HEX values with button[3]=0 (seconds=45, minutes=23, hours=7)"
    )
    assert int(dut.HEX0.value) == seg(5), (
        f"HEX0 (seconds ones=5): expected {seg(5):#09b}, got {int(dut.HEX0.value):#09b}"
    )
    assert int(dut.HEX1.value) == seg(4), (
        f"HEX1 (seconds tens=4): expected {seg(4):#09b}, got {int(dut.HEX1.value):#09b}"
    )
    assert int(dut.HEX2.value) == seg(3), (
        f"HEX2 (minutes ones=3): expected {seg(3):#09b}, got {int(dut.HEX2.value):#09b}"
    )
    assert int(dut.HEX3.value) == seg(2), (
        f"HEX3 (minutes tens=2): expected {seg(2):#09b}, got {int(dut.HEX3.value):#09b}"
    )
    assert int(dut.HEX4.value) == seg(7), (
        f"HEX4 (hours ones=7):   expected {seg(7):#09b}, got {int(dut.HEX4.value):#09b}"
    )
    assert int(dut.HEX5.value) == seg(0), (
        f"HEX5 (hours tens=0):   expected {seg(0):#09b}, got {int(dut.HEX5.value):#09b}"
    )


@cocotb.test()
async def test_display_values_button3_high(dut):
    """With button[3]=1 (KEY[3] pressed), verify all six HEX outputs.

    user_top drives: seconds=59, minutes=38, hours=16.
    """
    cocotb.start_soon(Clock(dut.CLOCK_50, 20, unit="ns").start())
    dut.SW.value = 0
    await set_keys(dut, pressed_mask=0b1000)

    cocotb.log.info(
        "Test: HEX values with button[3]=1 (seconds=59, minutes=38, hours=16)"
    )
    assert int(dut.HEX0.value) == seg(9), (
        f"HEX0 (seconds ones=9): expected {seg(9):#09b}, got {int(dut.HEX0.value):#09b}"
    )
    assert int(dut.HEX1.value) == seg(5), (
        f"HEX1 (seconds tens=5): expected {seg(5):#09b}, got {int(dut.HEX1.value):#09b}"
    )
    assert int(dut.HEX2.value) == seg(8), (
        f"HEX2 (minutes ones=8): expected {seg(8):#09b}, got {int(dut.HEX2.value):#09b}"
    )
    assert int(dut.HEX3.value) == seg(3), (
        f"HEX3 (minutes tens=3): expected {seg(3):#09b}, got {int(dut.HEX3.value):#09b}"
    )
    assert int(dut.HEX4.value) == seg(6), (
        f"HEX4 (hours ones=6):   expected {seg(6):#09b}, got {int(dut.HEX4.value):#09b}"
    )
    assert int(dut.HEX5.value) == seg(1), (
        f"HEX5 (hours tens=1):   expected {seg(1):#09b}, got {int(dut.HEX5.value):#09b}"
    )


@cocotb.test()
async def test_blanking(dut):
    """Pressing KEY[0/1/2] blanks the hours/minutes/seconds display respectively."""
    cocotb.start_soon(Clock(dut.CLOCK_50, 20, unit="ns").start())
    dut.SW.value = 0
    await set_keys(dut, pressed_mask=0b0000)

    # KEY[0] pressed -> button[0]=1 -> blank_hours -> HEX4/HEX5 off
    cocotb.log.info("Test: KEY[0] -> blank_hours -> HEX4 and HEX5 off")
    await set_keys(dut, pressed_mask=0b0001)
    assert int(dut.HEX4.value) == ALL_OFF, "blank_hours: HEX4 should be off"
    assert int(dut.HEX5.value) == ALL_OFF, "blank_hours: HEX5 should be off"
    assert int(dut.HEX2.value) != ALL_OFF, "blank_hours: HEX2 should not be off"
    assert int(dut.HEX0.value) != ALL_OFF, "blank_hours: HEX0 should not be off"
    await set_keys(dut, pressed_mask=0b0000)

    # KEY[1] pressed -> button[1]=1 -> blank_minutes -> HEX2/HEX3 off
    cocotb.log.info("Test: KEY[1] -> blank_minutes -> HEX2 and HEX3 off")
    await set_keys(dut, pressed_mask=0b0010)
    assert int(dut.HEX2.value) == ALL_OFF, "blank_minutes: HEX2 should be off"
    assert int(dut.HEX3.value) == ALL_OFF, "blank_minutes: HEX3 should be off"
    assert int(dut.HEX4.value) != ALL_OFF, "blank_minutes: HEX4 should not be off"
    assert int(dut.HEX0.value) != ALL_OFF, "blank_minutes: HEX0 should not be off"
    await set_keys(dut, pressed_mask=0b0000)

    # KEY[2] pressed -> button[2]=1 -> blank_seconds -> HEX0/HEX1 off
    cocotb.log.info("Test: KEY[2] -> blank_seconds -> HEX0 and HEX1 off")
    await set_keys(dut, pressed_mask=0b0100)
    assert int(dut.HEX0.value) == ALL_OFF, "blank_seconds: HEX0 should be off"
    assert int(dut.HEX1.value) == ALL_OFF, "blank_seconds: HEX1 should be off"
    assert int(dut.HEX2.value) != ALL_OFF, "blank_seconds: HEX2 should not be off"
    assert int(dut.HEX4.value) != ALL_OFF, "blank_seconds: HEX4 should not be off"
    await set_keys(dut, pressed_mask=0b0000)
