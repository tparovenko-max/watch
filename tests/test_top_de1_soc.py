import pytest
from conftest import rtl_exists

SOURCES = [
    "key_synchroniser.sv",
    "user_top.sv",
    "binary_to_bcd.sv",
    "seven_segment.sv",
    "decimal_display_driver.sv",
    "top_de1_soc.sv",
]


@pytest.mark.skipif(
    not rtl_exists("top_de1_soc.sv"),
    reason="top_de1_soc not implemented yet",
)
def test_top_de1_soc(cocotb_runner):
    """Test top_de1_soc: SW passthrough, display values, and blanking."""
    cocotb_runner(
        top="top_de1_soc",
        sources=SOURCES,
        test_module="tb_top_de1_soc",
    )
