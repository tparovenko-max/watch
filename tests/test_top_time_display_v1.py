import pytest
from conftest import rtl_exists

SOURCES = [
    "up_down_counter.sv",
    "mod_n_counter.sv",
    "restartable_rate_generator.sv",
    "hms_counter.sv",
    "binary_to_bcd.sv",
    "seven_segment.sv",
    "top_time_display_v1.sv",
]


@pytest.mark.skipif(
    not rtl_exists("top_time_display_v1.sv"),
    reason="top_time_display_v1 module not implemented yet",
)
def test_top_time_display_v1(cocotb_runner):
    """Test top_time_display_v1: rst wiring, SW mux, and HEX output validity."""
    cocotb_runner(
        top="top_time_display_v1",
        sources=SOURCES,
        test_module="tb_top_time_display_v1",
        parameters={"CYCLES_PER_SECOND": 50_000},
    )
