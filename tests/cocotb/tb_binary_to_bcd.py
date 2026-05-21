import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_binary_to_bcd(dut):
    """Test binary_to_bcd for all valid inputs (0--99)."""
    cocotb.log.info("Test: all values 0-99")
    for n in range(100):
        dut.bin.value = n
        await Timer(1, unit="ns")
        actual_tens = int(dut.tens.value)
        actual_ones = int(dut.ones.value)
        expected_tens = n // 10
        expected_ones = n % 10
        assert actual_tens == expected_tens, (
            f"bin={n}: expected tens={expected_tens}, got {actual_tens}"
        )
        assert actual_ones == expected_ones, (
            f"bin={n}: expected ones={expected_ones}, got {actual_ones}"
        )
