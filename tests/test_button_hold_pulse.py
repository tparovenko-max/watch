import pytest
from conftest import rtl_exists


@pytest.mark.skipif(
    not rtl_exists("button_hold_pulse.sv"),
    reason="button_hold_pulse not implemented yet",
)
def test_button_hold_pulse(cocotb_runner):
    """Test button_hold_pulse."""
    cocotb_runner(
        top="button_hold_pulse",
        sources=[
            "button_hold_pulse.sv",
            "button_hold_detect.sv",
            "rising_edge_detector.sv",
            "mod_n_counter.sv",
        ],
        test_module="tb_button_hold_pulse",
        parameters={"HOLD_CYCLES": 5},
    )
