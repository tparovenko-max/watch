import pytest
from conftest import rtl_exists

SOURCES = [
    "binary_to_bcd.sv",
    "seven_segment.sv",
    "decimal_display_driver.sv",
]


@pytest.mark.skipif(
    not rtl_exists("decimal_display_driver.sv"),
    reason="decimal_display_driver module not implemented yet",
)
def test_decimal_display_driver(cocotb_runner):
    """Test decimal_display_driver: spot-check values, blanking, and channel independence."""
    cocotb_runner(
        top="decimal_display_driver",
        sources=SOURCES,
        test_module="tb_decimal_display_driver",
    )
