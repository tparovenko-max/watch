import pytest
from conftest import rtl_exists


@pytest.mark.skipif(
    not rtl_exists("rising_edge_detector.sv"),
    reason="rising_edge_detector not implemented yet",
)
def test_rising_edge_detector(cocotb_runner):
    """Test rising_edge_detector."""
    cocotb_runner(
        top="rising_edge_detector",
        sources=["rising_edge_detector.sv"],
        test_module="tb_rising_edge_detector",
    )
