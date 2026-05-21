import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

CLK_PERIOD_NS = 10
SETTLE_NS = 1
MID_CYCLE_DELAY_NS = (CLK_PERIOD_NS // 2) - SETTLE_NS


def start_clock(dut):
    """Initialise DUT inputs and start a deterministic clock."""
    dut.run.value = 0
    dut.clk.value = 0
    Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start()


async def settle():
    """Wait for registered outputs to settle after an edge."""
    await Timer(SETTLE_NS, unit="ns")


async def step(dut):
    """Advance one clock cycle and wait for registered outputs to settle."""
    await RisingEdge(dut.clk)
    await settle()


async def reset_dut(dut):
    """Hold run low long enough for the counter to reset to 0."""
    dut.run.value = 0
    for _ in range(3):
        await step(dut)


@cocotb.test()
async def test_cycle_count_parameter(dut):
    """CYCLE_COUNT parameter is a positive integer >= 1."""
    N = int(dut.CYCLE_COUNT.value)
    assert N >= 1, f"CYCLE_COUNT must be >= 1, got {N}"


@cocotb.test()
async def test_port_widths(dut):
    """tick is a 1-bit output."""
    start_clock(dut)
    dut.run.value = 0
    await RisingEdge(dut.clk)

    assert len(dut.tick) == 1, f"tick should be 1 bit wide, got {len(dut.tick)}"


@cocotb.test()
async def test_tick_low_when_not_running(dut):
    """tick stays low for any number of cycles when run is low (including N=1)."""
    start_clock(dut)
    N = int(dut.CYCLE_COUNT.value)
    dut.run.value = 0
    await RisingEdge(dut.clk)

    for _ in range(N + 2):
        await step(dut)
        assert int(dut.tick.value) == 0, f"tick must stay low when run is low (N={N})"


@cocotb.test()
async def test_tick_fires_and_period(dut):
    """tick fires at the right time and repeats with the correct period.

    For CYCLE_COUNT=1 tick is permanently high while run is asserted.
    For CYCLE_COUNT>1 the first tick fires after CYCLE_COUNT-1 enabled
    clock edges; subsequent ticks repeat every CYCLE_COUNT edges.
    """
    start_clock(dut)
    N = int(dut.CYCLE_COUNT.value)
    await reset_dut(dut)

    dut.run.value = 1

    if N == 1:
        # Tick is permanently high while running
        for _ in range(5):
            await step(dut)
            assert (
                int(dut.tick.value) == 1
            ), "tick must be permanently high when CYCLE_COUNT=1 and run=1"
        return

    # First period: tick fires on the (N-1)-th enabled edge
    first_fire = N - 1
    for i in range(first_fire - 1):
        await step(dut)
        assert (
            int(dut.tick.value) == 0
        ), f"tick must stay low before cycle {first_fire} (cycle {i + 1})"
    await step(dut)
    assert (
        int(dut.tick.value) == 1
    ), f"tick must assert on the {first_fire}-th enabled clock edge"

    # Subsequent periods: N edges each (one reset-cycle overhead)
    for period in range(2, 4):
        for i in range(N - 1):
            await step(dut)
            assert (
                int(dut.tick.value) == 0
            ), f"period {period}: tick must be low at cycle {i + 1}"
        await step(dut)
        assert int(dut.tick.value) == 1, f"tick must fire at end of period {period}"


@cocotb.test()
async def test_tick_one_cycle_wide(dut):
    """tick is exactly one clock cycle wide (skipped for CYCLE_COUNT=1)."""
    start_clock(dut)
    N = int(dut.CYCLE_COUNT.value)

    if N == 1:
        return  # tick is permanently high; one-cycle-wide test does not apply

    await reset_dut(dut)
    dut.run.value = 1

    for _ in range(N - 2):
        await step(dut)
    await step(dut)
    assert int(dut.tick.value) == 1, "tick must be high on the firing cycle"

    await step(dut)
    assert int(dut.tick.value) == 0, "tick must deassert after exactly one cycle"


@cocotb.test()
async def test_counter_resets_on_stop(dut):
    """Stopping mid-count resets the counter; re-enabling requires a full period."""
    start_clock(dut)
    N = int(dut.CYCLE_COUNT.value)

    if N == 1:
        return  # no mid-count concept when tick is always high

    await reset_dut(dut)
    first_fire = N - 1

    # Count partway through the first period then stop
    dut.run.value = 1
    for _ in range(first_fire - 2):  # stop 2 steps before the tick
        await step(dut)
    dut.run.value = 0
    await step(dut)
    assert int(dut.tick.value) == 0, "tick must not fire when stopped mid-count"

    # Re-enable: counter was reset to 0; must take a full first_fire edges
    dut.run.value = 1
    for i in range(first_fire - 1):
        await step(dut)
        assert int(dut.tick.value) == 0, (
            f"after re-enable, tick must stay low for {first_fire} cycles "
            f"(cycle {i + 1}); counter did not reset"
        )
    await step(dut)
    assert (
        int(dut.tick.value) == 1
    ), f"tick must fire after {first_fire} edges following re-enable"


@cocotb.test()
async def test_moore_fsm(dut):
    """tick has no combinational dependence on run (Moore FSM, including N=1).

    Toggling run between rising edges must not immediately change tick.
    """
    start_clock(dut)
    N = int(dut.CYCLE_COUNT.value)

    await reset_dut(dut)

    if N == 1:
        # For N=1, tick should only change on clock edge, not immediately when run toggles
        # Set run=0, tick should be low
        dut.run.value = 0
        await step(dut)
        assert int(dut.tick.value) == 0, "tick must be low when run is low (N=1)"
        # Set run=1, tick should go high only after clock edge
        await Timer(MID_CYCLE_DELAY_NS, unit="ns")
        dut.run.value = 1
        await settle()
        assert int(dut.tick.value) == 0, "tick must not change immediately when run goes high (N=1)"
        await RisingEdge(dut.clk)
        await settle()
        assert int(dut.tick.value) == 1, "tick must go high after clock edge when run goes high (N=1)"
        # Now toggle run low mid-cycle, tick should not change until next clock edge
        await Timer(MID_CYCLE_DELAY_NS, unit="ns")
        dut.run.value = 0
        await settle()
        assert int(dut.tick.value) == 1, "tick must not change immediately when run goes low (N=1)"
        await RisingEdge(dut.clk)
        await settle()
        assert int(dut.tick.value) == 0, "tick must go low after clock edge when run goes low (N=1)"
        return

    # N > 1 case (original test)
    # Bring the counter to count == N-1 so that tick is high
    dut.run.value = 1
    first_fire = N - 1
    for _ in range(first_fire - 1):
        await step(dut)

    await RisingEdge(dut.clk)
    await settle()
    assert int(dut.tick.value) == 1, "Setup: tick must be high to run Moore test"

    tick_before = int(dut.tick.value)

    # Toggle run mid-cycle to check there is no combinational output change.
    await Timer(MID_CYCLE_DELAY_NS, unit="ns")
    dut.run.value = 0
    await settle()

    assert int(dut.tick.value) == tick_before, (
        "Moore FSM violation: tick changed immediately when 'run' toggled "
        "between clock edges. Output must only change on a clock edge."
    )

    # After the next rising edge with run=0, counter resets and tick falls
    await RisingEdge(dut.clk)
    await settle()
    assert int(dut.tick.value) == 0, "After clock edge with run=0, tick must be low"


@cocotb.test()
async def test_comprehensive(dut):
    """Comprehensive test reading CYCLE_COUNT from the DUT at runtime.

    Covers: CYCLE_COUNT=1 edge case, tick period, pulse width,
    stop-and-restart, and no combinational run->tick dependence.
    """
    start_clock(dut)
    dut.run.value = 1
    await RisingEdge(dut.clk)

    N = int(dut.CYCLE_COUNT.value)
    cocotb.log.info(f"Testing restartable_rate_generator with CYCLE_COUNT={N}")

    # --- CYCLE_COUNT=1: tick must be permanently high ---
    if N == 1:
        cocotb.log.info("CYCLE_COUNT=1: tick must be permanently high")
        for _ in range(10):
            await step(dut)
            assert (
                int(dut.tick.value) == 1
            ), "tick must be permanently high when CYCLE_COUNT=1"
        return

    # Reset to a known state
    dut.run.value = 0
    await step(dut)
    dut.run.value = 1

    # --- Tick period: exactly N cycles ---
    cocotb.log.info(f"Tick period: expected {N} cycles")
    num_periods = 4
    tick_cycles = []
    for i in range(num_periods * N):
        await step(dut)
        if int(dut.tick.value) == 1:
            tick_cycles.append(i)
    assert len(tick_cycles) == num_periods, (
        f"expected {num_periods} ticks in {num_periods * N} cycles, "
        f"got {len(tick_cycles)}"
    )
    for i in range(len(tick_cycles) - 1):
        assert tick_cycles[i + 1] - tick_cycles[i] == N, (
            f"tick period should be {N} cycles, "
            f"measured {tick_cycles[i + 1] - tick_cycles[i]}"
        )

    # --- Tick is high for exactly one cycle ---
    while int(dut.tick.value) == 0:
        await step(dut)
    await step(dut)
    assert int(dut.tick.value) == 0, "tick must be low the cycle after it was high"

    # --- Stop suppresses the next tick and restarts the period ---
    cocotb.log.info("Stop suppresses tick; next tick is N-1 cycles after restart")
    for _ in range(N - 2):
        await step(dut)
    assert int(dut.tick.value) == 0, "tick should not be high before run is deasserted"
    dut.run.value = 0
    await step(dut)
    assert (
        int(dut.tick.value) == 0
    ), "tick must not be asserted on the clock edge where run is deasserted"
    dut.run.value = 1
    for i in range(N - 2):
        await step(dut)
        assert (
            int(dut.tick.value) == 0
        ), f"tick must not be asserted {i + 1} cycle(s) after restart"
    await step(dut)
    assert (
        int(dut.tick.value) == 1
    ), f"tick must be asserted exactly {N - 1} cycles after restart"

    # --- run->tick has no combinational dependence ---
    cocotb.log.info("run->tick has no combinational dependence")
    dut.run.value = 0
    await step(dut)
    dut.run.value = 1
    await RisingEdge(dut.clk)
    await settle()
    tick_before = int(dut.tick.value)
    await Timer(MID_CYCLE_DELAY_NS, unit="ns")
    dut.run.value = 0
    await settle()
    assert (
        int(dut.tick.value) == tick_before
    ), "tick changed immediately after mid-cycle run toggle"
    await RisingEdge(dut.clk)
    await settle()
    assert (
        int(dut.tick.value) == 0
    ), "tick must be low on the first rising edge after run is deasserted"
    dut.run.value = 1
