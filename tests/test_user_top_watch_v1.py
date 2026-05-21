import pytest
from conftest import rtl_exists

SOURCES = [
    "up_down_counter.sv",
    "restartable_rate_generator.sv",
    "editable_counter.sv",
    "rising_edge_detector.sv",
    "button_hold_detect.sv",
    "button_hold_pulse.sv",
    "arming_latch.sv",
    "mod_n_counter.sv",
    "edit_mode_selector.sv",
    "pwm_generator.sv",
    "user_top_watch_v1.sv",
]

CYCLES_PER_SECOND = 3  # accelerated clock for simulation; non-power-of-two exercises wrap logic


@pytest.mark.skipif(
    not rtl_exists("user_top_watch_v1.sv"),
    reason="user_top_watch_v1 module not implemented yet",
)
def test_user_top_watch_v1(cocotb_runner):
    """Timekeeping feature: seconds/minutes/hours counting and rollovers."""
    cocotb_runner(
        top="user_top_watch_v1",
        sources=SOURCES,
        test_module="tb_user_top_watch_v1",
        parameters={"CYCLES_PER_SECOND": CYCLES_PER_SECOND},
    )
