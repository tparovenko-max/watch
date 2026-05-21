import math

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer


async def tick(dut):
    """Advance one clock cycle and wait for outputs to settle."""
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def tick_n(dut, n):
    """Advance n clock cycles.

    Uses ClockCycles for large n so the simulator advances natively without
    a Python coroutine suspension per cycle --- critical for keeping the
    H24_M60_S60 configuration fast.
    """
    if n <= 0:
        return
    await ClockCycles(dut.clk, n)
    await Timer(1, unit="ns")


@cocotb.test()
async def test_hms_counter(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await RisingEdge(dut.clk)  # let initial block settle

    N_HOURS   = int(dut.N_HOURS.value)
    N_MINUTES = int(dut.N_MINUTES.value)
    N_SECONDS = int(dut.N_SECONDS.value)
    cocotb.log.info(
        f"Testing hms_counter with N_HOURS={N_HOURS}, "
        f"N_MINUTES={N_MINUTES}, N_SECONDS={N_SECONDS}"
    )

    # --- output port widths match $clog2 of parameters ---
    cocotb.log.info("Test 0: Output port widths are correct")
    assert len(dut.hours)   == math.ceil(math.log2(N_HOURS)),   \
        f"hours should be {math.ceil(math.log2(N_HOURS))} bits wide"
    assert len(dut.minutes) == math.ceil(math.log2(N_MINUTES)), \
        f"minutes should be {math.ceil(math.log2(N_MINUTES))} bits wide"
    assert len(dut.seconds) == math.ceil(math.log2(N_SECONDS)), \
        f"seconds should be {math.ceil(math.log2(N_SECONDS))} bits wide"

    # --- enable=0 holds all outputs at 0 ---
    cocotb.log.info("Test 1: enable=0 holds all outputs at 0")
    dut.enable.value = 0
    assert int(dut.hours.value)   == 0, "hours should initialise to 0"
    assert int(dut.minutes.value) == 0, "minutes should initialise to 0"
    assert int(dut.seconds.value) == 0, "seconds should initialise to 0"
    for _ in range(5):
        await tick(dut)
    assert int(dut.hours.value)   == 0, "hours should not change when disabled"
    assert int(dut.minutes.value) == 0, "minutes should not change when disabled"
    assert int(dut.seconds.value) == 0, "seconds should not change when disabled"

    # --- seconds counts up each enabled cycle ---
    cocotb.log.info("Test 2: Seconds counts up each enabled clock cycle")
    dut.enable.value = 1
    await tick(dut)
    assert int(dut.seconds.value) == 1, "seconds should be 1 after first enabled tick"
    assert int(dut.minutes.value) == 0, "minutes should not change yet"
    assert int(dut.hours.value)   == 0, "hours should not change yet"

    # --- seconds rolls over and increments minutes ---
    cocotb.log.info(
        f"Test 3: Seconds rolls over from {N_SECONDS - 1} to 0 and increments minutes"
    )
    # Advance to the last second of the first minute
    await tick_n(dut, N_SECONDS - 2)
    assert int(dut.seconds.value) == N_SECONDS - 1, \
        f"seconds should be {N_SECONDS - 1} before rollover"
    assert int(dut.minutes.value) == 0, "minutes should still be 0"
    # One more tick: seconds wraps to 0, minutes increments to 1
    await tick(dut)
    assert int(dut.seconds.value) == 0, "seconds should wrap to 0"
    assert int(dut.minutes.value) == 1, "minutes should increment to 1 on second rollover"
    assert int(dut.hours.value)   == 0, "hours should not change yet"

    # --- minutes rolls over and increments hours ---
    cocotb.log.info(
        f"Test 4: Minutes rolls over from {N_MINUTES - 1} to 0 and increments hours"
    )
    # Advance through the remaining minutes of the first hour.
    # minutes is already 1 (from test 3), so advance N_MINUTES-2 more complete minutes.
    await tick_n(dut, N_SECONDS * (N_MINUTES - 2))
    assert int(dut.minutes.value) == N_MINUTES - 1, \
        f"minutes should be {N_MINUTES - 1} before rollover"
    assert int(dut.seconds.value) == 0, "seconds should be 0 at minute boundary"
    assert int(dut.hours.value)   == 0, "hours should still be 0"
    # One more second rollover tips minutes over
    await tick_n(dut, N_SECONDS)
    assert int(dut.minutes.value) == 0, "minutes should wrap to 0"
    assert int(dut.hours.value)   == 1, "hours should increment to 1 on minute rollover"

    # --- full cycle: hours rolls over back to 0 ---
    # Skip for large configs: rollover logic is parametric, so the smaller
    # configs (H2_M2_S2 and H3_M4_S5) already cover this code path.
    if N_HOURS * N_MINUTES * N_SECONDS > 10_000:
        cocotb.log.info(
            f"Test 5: Skipped for large config "
            f"(N_HOURS={N_HOURS}, N_MINUTES={N_MINUTES}, N_SECONDS={N_SECONDS})"
        )
    else:
        cocotb.log.info(
            f"Test 5: Full cycle --- hours rolls over from {N_HOURS - 1} to 0"
        )
        # Advance through the remaining hours.
        # hours is already 1 (from test 4), so advance N_HOURS-2 more complete hours.
        await tick_n(dut, N_SECONDS * N_MINUTES * (N_HOURS - 2))
        assert int(dut.hours.value)   == N_HOURS - 1, \
            f"hours should be {N_HOURS - 1} before rollover"
        assert int(dut.minutes.value) == 0
        assert int(dut.seconds.value) == 0
        # One complete minute cycle tips hours over
        await tick_n(dut, N_SECONDS * N_MINUTES)
        assert int(dut.hours.value)   == 0, f"hours should wrap from {N_HOURS - 1} to 0"
        assert int(dut.minutes.value) == 0
        assert int(dut.seconds.value) == 0

    # --- enable=0 mid-count holds all outputs ---
    cocotb.log.info("Test 6: enable=0 mid-count holds all outputs")
    dut.enable.value = 1
    await tick_n(dut, 3)
    dut.enable.value = 0
    snap_h = int(dut.hours.value)
    snap_m = int(dut.minutes.value)
    snap_s = int(dut.seconds.value)
    for _ in range(5):
        await tick(dut)
    assert int(dut.hours.value)   == snap_h, "hours should not change when disabled"
    assert int(dut.minutes.value) == snap_m, "minutes should not change when disabled"
    assert int(dut.seconds.value) == snap_s, "seconds should not change when disabled"
