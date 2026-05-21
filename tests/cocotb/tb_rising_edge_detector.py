import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def step(dut):
    """Advance one clock cycle and wait for outputs to settle."""
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def set_sig(dut, val):
    """Set sig_in and wait for combinational outputs to settle."""
    dut.sig_in.value = val
    await Timer(1, unit="ns")


@cocotb.test()
async def test_rising_edge_detector(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.sig_in.value = 0
    await RisingEdge(dut.clk)  # let initial block settle

    # --- Test 0: rise is exactly 1 bit wide ---
    cocotb.log.info("Test 0: rise is 1 bit wide")
    assert len(dut.rise) == 1, f"rise should be 1 bit wide, got {len(dut.rise)}"

    # --- Test 1: rise is low when sig_in is stable low ---
    cocotb.log.info("Test 1: rise is low when sig_in is stable low")
    for _ in range(4):
        await step(dut)
        assert int(dut.rise.value) == 0, "rise must be low when sig_in is stable low"

    # --- Test 2: rise goes high immediately when sig_in rises ---
    # rise is combinational, so it responds before the next clock edge.
    cocotb.log.info("Test 2: rise goes high immediately when sig_in rises")
    await set_sig(dut, 1)
    assert int(dut.rise.value) == 1, (
        "rise must go high immediately (combinationally) when sig_in rises"
    )

    # --- Test 3: rise is high for exactly one clock cycle ---
    cocotb.log.info("Test 3: rise is high for exactly one clock cycle")
    await step(dut)  # sig_d captures sig_in=1
    assert int(dut.rise.value) == 0, (
        "rise must deassert on the cycle after sig_in rises"
    )
    await step(dut)
    assert int(dut.rise.value) == 0, (
        "rise must remain low while sig_in is held high"
    )

    # --- Test 4: rise does not assert on falling edge ---
    cocotb.log.info("Test 4: rise does not assert on falling edge of sig_in")
    await set_sig(dut, 0)
    assert int(dut.rise.value) == 0, (
        "rise must not assert when sig_in falls"
    )
    await step(dut)
    assert int(dut.rise.value) == 0, (
        "rise must remain low after sig_in falls"
    )

    # --- Test 5: rise asserts again on a second rising edge ---
    cocotb.log.info("Test 5: rise asserts again on a second rising edge")
    await set_sig(dut, 1)
    assert int(dut.rise.value) == 1, (
        "rise must assert again on a second rising edge of sig_in"
    )
    await step(dut)
    assert int(dut.rise.value) == 0, (
        "rise must deassert after the second rising edge"
    )

    # --- Test 6: rise does not assert when sig_in is already high at startup ---
    # Reset the delayed register by holding sig_in high for one cycle, then
    # verify rise does not assert on the next cycle (sig_in remains high).
    cocotb.log.info("Test 6: rise does not assert when sig_in is already high")
    await step(dut)  # sig_d=1, sig_in=1: rise=0
    assert int(dut.rise.value) == 0, (
        "rise must remain low when sig_in is held high across cycles"
    )
