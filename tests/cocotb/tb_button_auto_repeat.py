import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

# Must match the parameters passed by the test runner.
HOLD_CYCLES   = 8
REPEAT_CYCLES = 3
# Hold threshold passed to button_hold_detect inside the DUT.
# held goes high after this many consecutive held cycles.
QUAL_CYCLES = HOLD_CYCLES - REPEAT_CYCLES + 1   # = 6


async def step(dut):
    """Advance one clock cycle and wait for registered outputs to settle."""
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def reset_dut(dut):
    """Hold button low long enough for all state to reset."""
    dut.button.value = 0
    for _ in range(3):
        await step(dut)


@cocotb.test()
async def test_port_widths(dut):
    """pulse is a 1-bit output."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.button.value = 0
    await RisingEdge(dut.clk)

    assert len(dut.pulse) == 1, f"pulse should be 1 bit wide, got {len(dut.pulse)}"


@cocotb.test()
async def test_initial_pulse_on_press(dut):
    """pulse asserts immediately when button goes high, before any clock edge.

    rise = button & ~sig_d is combinational, so it fires the moment button
    goes high (while sig_d is still 0).  On the first clock edge sig_d catches
    up and rise falls.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    dut.button.value = 1
    await Timer(1, unit="ns")
    assert int(dut.pulse.value) == 1, (
        "pulse must assert immediately when button is pressed (combinational rise)"
    )

    await step(dut)
    assert int(dut.pulse.value) == 0, (
        "pulse must deassert on the first clock edge after press "
        "(sig_d catches up; held is not yet high)"
    )


@cocotb.test()
async def test_pulse_low_when_button_low(dut):
    """pulse stays low while button is never pressed."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    for _ in range(HOLD_CYCLES + 2):
        await step(dut)
        assert int(dut.pulse.value) == 0, "pulse must stay low when button is low"


@cocotb.test()
async def test_no_repeat_on_short_press(dut):
    """Releasing button before QUAL_CYCLES produces no pulse_train.

    The button must be held for at least QUAL_CYCLES = HOLD_CYCLES - REPEAT_CYCLES + 1
    consecutive cycles before held asserts.  A shorter press yields only the
    initial combinational pulse.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    dut.button.value = 1
    for i in range(QUAL_CYCLES - 1):   # hold for one cycle short of qualifying
        await step(dut)
        assert int(dut.pulse.value) == 0, (
            f"pulse must be low on cycle {i + 1} during a short press "
            f"(held requires {QUAL_CYCLES} cycles)"
        )
    dut.button.value = 0

    for _ in range(REPEAT_CYCLES + 1):
        await step(dut)
        assert int(dut.pulse.value) == 0, (
            "pulse must not fire after a short press is released"
        )


@cocotb.test()
async def test_first_repeat_fires_at_hold_cycles(dut):
    """pulse_train fires for the first time on the HOLD_CYCLES-th clock edge.

    The hold threshold and restartable_rate_generator first-fire delay are chosen so that
    QUAL_CYCLES + (REPEAT_CYCLES - 1) == HOLD_CYCLES exactly.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    dut.button.value = 1
    for i in range(HOLD_CYCLES - 1):
        await step(dut)
        assert int(dut.pulse.value) == 0, (
            f"pulse must be low before the {HOLD_CYCLES}-th edge (step {i + 1})"
        )

    await step(dut)
    assert int(dut.pulse.value) == 1, (
        f"pulse_train must fire on the {HOLD_CYCLES}-th clock edge after button press"
    )


@cocotb.test()
async def test_repeat_pulse_one_cycle_wide(dut):
    """Each repeat pulse is exactly one clock cycle wide."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    dut.button.value = 1
    for _ in range(HOLD_CYCLES - 1):
        await step(dut)
    await step(dut)
    assert int(dut.pulse.value) == 1, "first repeat must be high on the firing cycle"

    await step(dut)
    assert int(dut.pulse.value) == 0, "repeat pulse must deassert after exactly one cycle"


@cocotb.test()
async def test_pulse_train_periodic(dut):
    """While button is held, pulse_train repeats every REPEAT_CYCLES clock cycles."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    dut.button.value = 1
    periods = 3

    # Steps 1 to HOLD_CYCLES-1: no pulse
    for i in range(HOLD_CYCLES - 1):
        await step(dut)
        assert int(dut.pulse.value) == 0, (
            f"pulse must be low before the first repeat (step {i + 1})"
        )
    # Step HOLD_CYCLES: first repeat
    await step(dut)
    assert int(dut.pulse.value) == 1, "first repeat must fire at step HOLD_CYCLES"

    # Subsequent repeats: REPEAT_CYCLES steps apart
    for period in range(2, periods + 1):
        for i in range(REPEAT_CYCLES - 1):
            await step(dut)
            assert int(dut.pulse.value) == 0, (
                f"period {period}: pulse must be low at step {i + 1}"
            )
        await step(dut)
        assert int(dut.pulse.value) == 1, (
            f"period {period}: repeat pulse must fire"
        )


@cocotb.test()
async def test_no_pulse_after_release(dut):
    """After button is released, pulse ceases within one cycle.

    held is a registered signal, so it takes one clock edge to respond
    to button going low.  One extra timer advance can therefore occur on the
    transition edge.  After that single latency cycle, no further pulses fire.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Hold long enough to get a repeat firing
    dut.button.value = 1
    for _ in range(HOLD_CYCLES + REPEAT_CYCLES):
        await step(dut)

    dut.button.value = 0

    # Allow one cycle for the registered held signal to propagate the release
    await step(dut)

    # No further pulses should fire once the system has settled
    for _ in range(REPEAT_CYCLES + 1):
        await step(dut)
        assert int(dut.pulse.value) == 0, (
            "pulse must not fire after button has been released and settled"
        )


@cocotb.test()
async def test_repeat_restarts_after_release(dut):
    """Releasing and re-pressing button produces a fresh initial pulse and restart."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # First press: hold long enough for a repeat
    dut.button.value = 1
    for _ in range(HOLD_CYCLES):
        await step(dut)
    assert int(dut.pulse.value) == 1, "first press: repeat must fire at HOLD_CYCLES"

    # Release
    dut.button.value = 0
    await step(dut)   # latency cycle
    for _ in range(REPEAT_CYCLES + 1):
        await step(dut)
        assert int(dut.pulse.value) == 0, "pulse must cease after release"

    # Re-press: initial combinational pulse fires immediately
    dut.button.value = 1
    await Timer(1, unit="ns")
    assert int(dut.pulse.value) == 1, (
        "re-press must produce an immediate pulse (combinational rise)"
    )

    # Then steps 1 to HOLD_CYCLES-1: no pulse_train
    for i in range(HOLD_CYCLES - 1):
        await step(dut)
        assert int(dut.pulse.value) == 0, (
            f"re-press: pulse must be low before the {HOLD_CYCLES}-th edge (step {i + 1})"
        )

    # Step HOLD_CYCLES: repeat fires again
    await step(dut)
    assert int(dut.pulse.value) == 1, (
        "re-press: repeat must fire again at HOLD_CYCLES"
    )
