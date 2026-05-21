import pytest
from conftest import rtl_exists


@pytest.mark.skipif(
    not rtl_exists("button_auto_repeat.sv"),
    reason="button_auto_repeat not implemented yet",
)
def test_button_auto_repeat(cocotb_runner):
    """Test button_auto_repeat."""
    cocotb_runner(
        top="button_auto_repeat",
        sources=[
            "button_auto_repeat.sv",
            "rising_edge_detector.sv",
            "button_hold_detect.sv",
            "restartable_rate_generator.sv",
            "mod_n_counter.sv",
        ],
        test_module="tb_button_auto_repeat",
        parameters={"HOLD_CYCLES": 8, "REPEAT_CYCLES": 3},
    )
