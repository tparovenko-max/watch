import pytest
from conftest import rtl_exists


@pytest.mark.skipif(
    not rtl_exists("button_hold_detect.sv"),
    reason="button_hold_detect not implemented yet",
)
def test_button_hold_detect(cocotb_runner):
    """Test button_hold_detect."""
    cocotb_runner(
        top="button_hold_detect",
        sources=["button_hold_detect.sv", "mod_n_counter.sv"],
        test_module="tb_button_hold_detect",
        parameters={"HOLD_CYCLES": 3},
    )
