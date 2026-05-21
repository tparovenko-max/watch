import pytest
from conftest import rtl_exists


@pytest.mark.skipif(
    not rtl_exists("binary_to_bcd.sv"), reason="binary_to_bcd module not implemented yet"
)
def test_binary_to_bcd(cocotb_runner):
    """Test binary_to_bcd for all valid inputs (0--99)."""
    cocotb_runner(
        top="binary_to_bcd",
        sources=["binary_to_bcd.sv"],
        test_module="tb_binary_to_bcd",
    )
