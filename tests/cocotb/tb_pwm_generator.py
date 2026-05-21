import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def step(dut):
    """Advance one clock cycle and wait for outputs to settle."""
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


@cocotb.test()
async def test_pwm_generator(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value = 0
    await RisingEdge(dut.clk)  # let initial block settle

    PERIOD_CYCLES = int(dut.PERIOD_CYCLES.value)
    DUTY_CYCLES   = int(dut.DUTY_CYCLES.value)
    cocotb.log.info(
        f"Testing pwm_generator with PERIOD_CYCLES={PERIOD_CYCLES}, "
        f"DUTY_CYCLES={DUTY_CYCLES}"
    )

    # --- Test 0: pwm_out is exactly 1 bit wide ---
    cocotb.log.info("Test 0: pwm_out is 1 bit wide")
    assert len(dut.pwm_out) == 1, (
        f"pwm_out should be 1 bit wide, got {len(dut.pwm_out)}"
    )

    # --- reset to a known state ---
    dut.rst.value = 1
    await step(dut)  # counter resets to 0
    dut.rst.value = 0

    # --- Test 1: high and low cycle counts over one full period ---
    # After reset, the counter is 0.  Sample pwm_out at cycle 0, then step
    # through cycles 1 .. PERIOD_CYCLES-1, counting how many are high.
    cocotb.log.info(
        f"Test 1: pwm_out is high for {DUTY_CYCLES} cycles and low for "
        f"{PERIOD_CYCLES - DUTY_CYCLES} cycles per period"
    )
    high_count = 1 if int(dut.pwm_out.value) == 1 else 0
    for _ in range(PERIOD_CYCLES - 1):
        await step(dut)
        if int(dut.pwm_out.value) == 1:
            high_count += 1
    assert high_count == DUTY_CYCLES, (
        f"pwm_out should be high for {DUTY_CYCLES} cycles per period, "
        f"got {high_count}"
    )

    # --- Test 2: output wraps correctly after PERIOD_CYCLES cycles ---
    # After Test 1, we are one step before the end of the period.  One more
    # step should wrap the counter and restore pwm_out to its cycle-0 value.
    cocotb.log.info(f"Test 2: output wraps correctly after {PERIOD_CYCLES} cycles")
    expected_at_zero = 1 if DUTY_CYCLES > 0 else 0
    await step(dut)
    assert int(dut.pwm_out.value) == expected_at_zero, (
        f"after {PERIOD_CYCLES} cycles pwm_out should be {expected_at_zero} "
        f"(cycle-0 value), got {int(dut.pwm_out.value)}"
    )

    # --- Test 3: period is exactly PERIOD_CYCLES cycles ---
    # Skipped when DUTY_CYCLES is 0 or PERIOD_CYCLES (constant output; no edges).
    # Starting from cycle 0 (left by Test 2), step through the high region then
    # the low region, counting cycles until pwm_out rises again.
    if 0 < DUTY_CYCLES < PERIOD_CYCLES:
        cocotb.log.info(f"Test 3: period is exactly {PERIOD_CYCLES} cycles")
        cycle_count = 0
        await step(dut)
        cycle_count += 1                        # cycle 1
        while int(dut.pwm_out.value) == 1:      # step through remaining high region
            await step(dut)
            cycle_count += 1
        while int(dut.pwm_out.value) == 0:      # step through low region
            await step(dut)
            cycle_count += 1
        # Now at the next rising edge (cycle 0 again)
        assert cycle_count == PERIOD_CYCLES, (
            f"period should be {PERIOD_CYCLES} cycles, measured {cycle_count}"
        )
    else:
        cocotb.log.info(
            f"Test 3: skipped (DUTY_CYCLES={DUTY_CYCLES} is constant, no edges to measure)"
        )

    # --- Test 4: high cycle count is consistent over multiple periods ---
    cocotb.log.info("Test 4: high cycle count is consistent over 4 periods")
    num_periods = 4
    high_count = 0
    for _ in range(num_periods * PERIOD_CYCLES):
        await step(dut)
        if int(dut.pwm_out.value) == 1:
            high_count += 1
    assert high_count == num_periods * DUTY_CYCLES, (
        f"expected {num_periods * DUTY_CYCLES} high cycles over {num_periods} periods, "
        f"got {high_count}"
    )

    # --- Test 5: reset mid-period suppresses remaining cycles and restarts ---
    cocotb.log.info("Test 5: reset mid-period suppresses output and restarts the period")
    for _ in range(max(1, PERIOD_CYCLES // 2)):
        await step(dut)
    dut.rst.value = 1
    await step(dut)
    dut.rst.value = 0
    # Verify a full period from cycle 0
    high_count = 1 if int(dut.pwm_out.value) == 1 else 0
    for _ in range(PERIOD_CYCLES - 1):
        await step(dut)
        if int(dut.pwm_out.value) == 1:
            high_count += 1
    assert high_count == DUTY_CYCLES, (
        f"after reset, pwm_out should be high for {DUTY_CYCLES} cycles, "
        f"got {high_count}"
    )

    # --- Test 6: rst is synchronous, not asynchronous ---
    # Only testable when there is a low region (0 < DUTY_CYCLES < PERIOD_CYCLES):
    # advance into the low region, assert rst mid-cycle, and verify that pwm_out
    # does not immediately rise to its cycle-0 value (which would indicate async
    # reset).  It must only change on the next rising clock edge.
    if 0 < DUTY_CYCLES < PERIOD_CYCLES:
        cocotb.log.info("Test 6: rst is synchronous, not asynchronous")
        # Advance until pwm_out is low (inside the low region)
        while int(dut.pwm_out.value) != 0:
            await step(dut)
        # Assert rst mid-cycle (5 ns into the 10 ns period)
        await Timer(4, unit="ns")
        dut.rst.value = 1
        await Timer(1, unit="ns")
        assert int(dut.pwm_out.value) == 0, (
            "rst appears to be asynchronous: pwm_out rose immediately on rst assertion "
            "(expected no change until the next rising clock edge)"
        )
        # On the next rising edge the counter resets; pwm_out must reflect cycle 0
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        assert int(dut.pwm_out.value) == 1, (
            "pwm_out should be high (cycle 0) on the first rising edge after rst"
        )
        dut.rst.value = 0
    else:
        cocotb.log.info(
            f"Test 6: skipped (DUTY_CYCLES={DUTY_CYCLES} is constant, "
            "cannot detect async reset from output)"
        )
