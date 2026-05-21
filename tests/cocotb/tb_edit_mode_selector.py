import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

# Must match the HOLD_CYCLES parameter passed by the test runner.
HOLD_CYCLES = 5
# button_hold_detect asserts held after HOLD_CYCLES held edges.
# rising_edge_detector adds one further pipeline cycle before armed asserts.
ARM_CYCLES = HOLD_CYCLES + 1
# Short press duration: long enough to span one clock edge, short enough that
# the hold count never reaches HOLD_CYCLES and fires a long press.
SHORT_PRESS_CYCLES = 2


async def step(dut):
    """Advance one clock cycle and wait for registered outputs to settle."""
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def ensure_unarmed(dut):
    """Drive the DUT to a known unarmed state (mode_enable == 000).

    Releases the button and waits long enough for all pipeline state to flush
    (including button_hold_detect and the rising-edge detector).  If the
    arming latch was accidentally set by a previous test, up to three short
    presses cycle the mode counter to the disarm condition.
    """
    dut.button.value = 0
    for _ in range(ARM_CYCLES + 3):
        await step(dut)
    # If armed, short-press up to 3 times to reach the disarm condition
    for _ in range(3):
        if int(dut.mode_enable.value) == 0:
            break
        await short_press(dut)
    assert int(dut.mode_enable.value) == 0, (
        "ensure_unarmed: could not reach unarmed state"
    )


async def long_press(dut):
    """Hold button for ARM_CYCLES+1 cycles so that armed asserts, then release."""
    dut.button.value = 1
    for _ in range(ARM_CYCLES + 1):
        await step(dut)
    dut.button.value = 0
    await step(dut)


async def short_press(dut):
    """Pulse button for SHORT_PRESS_CYCLES cycles then release."""
    dut.button.value = 1
    for _ in range(SHORT_PRESS_CYCLES):
        await step(dut)
    dut.button.value = 0
    await step(dut)


@cocotb.test()
async def test_port_widths(dut):
    """mode_enable is a 3-bit output."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.button.value = 0
    await RisingEdge(dut.clk)

    assert len(dut.mode_enable) == 3, (
        f"mode_enable should be 3 bits wide, got {len(dut.mode_enable)}"
    )


@cocotb.test()
async def test_mode_enable_zero_initially(dut):
    """mode_enable is 000 before any button press."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.button.value = 0
    await RisingEdge(dut.clk)

    for _ in range(ARM_CYCLES + 2):
        await step(dut)
        assert int(dut.mode_enable.value) == 0b000, (
            "mode_enable must be 000 when button is never pressed"
        )


@cocotb.test()
async def test_short_presses_ignored_when_unarmed(dut):
    """Short presses before arming do not change mode_enable."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await ensure_unarmed(dut)

    for _ in range(3):
        await short_press(dut)
        assert int(dut.mode_enable.value) == 0b000, (
            "mode_enable must remain 000 after a short press when not armed"
        )


@cocotb.test()
async def test_mode_enable_zero_during_long_press(dut):
    """mode_enable stays 000 for the first ARM_CYCLES-1 cycles of a long press."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await ensure_unarmed(dut)

    dut.button.value = 1
    for i in range(ARM_CYCLES - 1):
        await step(dut)
        assert int(dut.mode_enable.value) == 0b000, (
            f"mode_enable must be 000 before armed asserts (step {i + 1})"
        )


@cocotb.test()
async def test_long_press_arms(dut):
    """After ARM_CYCLES held edges, mode_enable becomes 001."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await ensure_unarmed(dut)

    dut.button.value = 1
    for _ in range(ARM_CYCLES):
        await step(dut)

    assert int(dut.mode_enable.value) == 0b001, (
        f"mode_enable must be 001 after {ARM_CYCLES} held clock edges"
    )


@cocotb.test()
async def test_mode_enable_stable_after_arm(dut):
    """mode_enable holds at 001 while button remains held and after release."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await ensure_unarmed(dut)

    await long_press(dut)

    # After release, armed and count are unchanged
    for _ in range(3):
        await step(dut)
        assert int(dut.mode_enable.value) == 0b001, (
            "mode_enable must remain 001 after arming long press is released"
        )


@cocotb.test()
async def test_short_presses_cycle_modes(dut):
    """Three short presses while armed cycle mode_enable 001 -> 010 -> 100 -> 000."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await ensure_unarmed(dut)

    await long_press(dut)
    assert int(dut.mode_enable.value) == 0b001, "mode_enable must be 001 after arming"

    await short_press(dut)
    assert int(dut.mode_enable.value) == 0b010, (
        "mode_enable must be 010 after first short press"
    )

    await short_press(dut)
    assert int(dut.mode_enable.value) == 0b100, (
        "mode_enable must be 100 after second short press"
    )

    await short_press(dut)
    assert int(dut.mode_enable.value) == 0b000, (
        "mode_enable must be 000 after third short press (disarm)"
    )


@cocotb.test()
async def test_short_presses_ignored_after_disarm(dut):
    """Short presses after disarm do not change mode_enable."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await ensure_unarmed(dut)

    # Arm and cycle through all three modes to disarm
    await long_press(dut)
    for _ in range(3):
        await short_press(dut)
    assert int(dut.mode_enable.value) == 0b000, "must be disarmed before this test"

    for _ in range(3):
        await short_press(dut)
        assert int(dut.mode_enable.value) == 0b000, (
            "mode_enable must remain 000 after a short press when disarmed"
        )


@cocotb.test()
async def test_rearming(dut):
    """After disarm, a second long press re-arms and restores mode_enable to 001."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await ensure_unarmed(dut)

    # First arm-and-disarm cycle
    await long_press(dut)
    for _ in range(3):
        await short_press(dut)
    assert int(dut.mode_enable.value) == 0b000, "must be disarmed before rearming test"

    # Second long press
    await long_press(dut)
    assert int(dut.mode_enable.value) == 0b001, (
        "mode_enable must return to 001 after a second long press"
    )

    # Confirm modes cycle again correctly
    await short_press(dut)
    assert int(dut.mode_enable.value) == 0b010, (
        "mode_enable must advance to 010 on first short press after rearming"
    )
