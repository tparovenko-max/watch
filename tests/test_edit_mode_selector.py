import pytest
from conftest import rtl_exists


@pytest.mark.skipif(
    not rtl_exists("edit_mode_selector.sv"),
    reason="edit_mode_selector not implemented yet",
)
def test_edit_mode_selector(cocotb_runner):
    """Test edit_mode_selector."""
    cocotb_runner(
        top="edit_mode_selector",
        sources=[
            "edit_mode_selector.sv",
            "button_hold_pulse.sv",
            "button_hold_detect.sv",
            "rising_edge_detector.sv",
            "arming_latch.sv",
            "mod_n_counter.sv",
        ],
        test_module="tb_edit_mode_selector",
        parameters={"HOLD_CYCLES": 5},
    )
