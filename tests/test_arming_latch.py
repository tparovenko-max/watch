import pytest
from conftest import rtl_exists


@pytest.mark.skipif(
    not rtl_exists("arming_latch.sv"),
    reason="arming_latch not implemented yet",
)
def test_arming_latch(cocotb_runner):
    """Test arming_latch."""
    cocotb_runner(
        top="arming_latch",
        sources=["arming_latch.sv"],
        test_module="tb_arming_latch",
    )
