import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def step(dut):
    """Advance one clock cycle and wait for registered outputs to settle."""
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


@cocotb.test()
async def test_mod_n_counter(dut):
    n = int(dut.N.value)
    width = int(dut.WIDTH.value)

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value = 0
    dut.enable.value = 0
    await RisingEdge(dut.clk)  # let initial state settle

    # --- Test 0: count is WIDTH bits wide ---
    cocotb.log.info("Test 0: count is WIDTH bits wide")
    assert len(dut.count) == width, (
        f"count should be {width} bits wide, got {len(dut.count)}"
    )

    # --- Test 1: count starts at zero ---
    cocotb.log.info("Test 1: count starts at zero")
    await step(dut)
    assert int(dut.count.value) == 0, "count must be zero initially"

    # --- Test 2: count does not advance when enable is low ---
    cocotb.log.info("Test 2: count holds when enable is low")
    for _ in range(3):
        await step(dut)
        assert int(dut.count.value) == 0, "count must not advance when enable is low"

    # --- Test 3: count advances each cycle while enable is high ---
    cocotb.log.info("Test 3: count advances with enable")
    dut.enable.value = 1
    for expected in range(1, n):
        await step(dut)
        assert int(dut.count.value) == expected, (
            f"expected count {expected}, got {int(dut.count.value)}"
        )

    # --- Test 4: count wraps from N-1 back to zero ---
    cocotb.log.info("Test 4: count wraps from N-1 to 0")
    assert int(dut.count.value) == n - 1, "count must be N-1 before wrap"
    await step(dut)
    assert int(dut.count.value) == 0, (
        f"count must wrap to 0 after reaching N-1 ({n - 1})"
    )

    # --- Test 5: full cycle repeats correctly ---
    cocotb.log.info("Test 5: full count cycle repeats")
    for expected in list(range(1, n)) + [0]:
        await step(dut)
        assert int(dut.count.value) == expected, (
            f"expected count {expected} on second cycle, got {int(dut.count.value)}"
        )

    # --- Test 6: enable gating holds count mid-sequence ---
    cocotb.log.info("Test 6: enable gating holds count mid-sequence")
    # Advance to a known mid-point
    await step(dut)  # count = 1
    await step(dut)  # count = 2
    held = int(dut.count.value)
    dut.enable.value = 0
    for _ in range(4):
        await step(dut)
        assert int(dut.count.value) == held, (
            f"count must hold at {held} while enable is low"
        )
    dut.enable.value = 1

    # --- Test 7: rst clears count immediately, regardless of enable ---
    cocotb.log.info("Test 7: rst clears count")
    # Reset to a known baseline, then advance to a predictable non-zero count
    dut.rst.value = 1
    await step(dut)
    dut.rst.value = 0
    await step(dut)  # count = 1
    await step(dut)  # count = 2
    assert int(dut.count.value) == 2, "count must be 2 before reset test"
    dut.rst.value = 1
    await step(dut)
    dut.rst.value = 0
    assert int(dut.count.value) == 0, (
        "count must be zero on the cycle after rst is asserted"
    )

    # --- Test 8: rst takes priority over enable ---
    cocotb.log.info("Test 8: rst takes priority over enable")
    # Advance to a predictable non-zero count
    await step(dut)  # count = 1
    await step(dut)  # count = 2
    assert int(dut.count.value) == 2, "count must be 2 before priority test"
    dut.rst.value = 1  # assert rst while enable remains high
    await step(dut)
    dut.rst.value = 0
    assert int(dut.count.value) == 0, (
        "rst must take priority over enable and clear count to zero"
    )

    # --- Test 9: counter resumes correctly after rst ---
    cocotb.log.info("Test 9: counter resumes correctly after rst")
    for expected in range(1, n):
        await step(dut)
        assert int(dut.count.value) == expected, (
            f"expected count {expected} after reset, got {int(dut.count.value)}"
        )
