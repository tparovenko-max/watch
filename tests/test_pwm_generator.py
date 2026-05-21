import pytest
from conftest import rtl_exists

CONFIGS = [
    {"PERIOD_CYCLES": 4, "DUTY_CYCLES": 0},  # 0%: always low
    {"PERIOD_CYCLES": 4, "DUTY_CYCLES": 1},  # 25%
    {"PERIOD_CYCLES": 4, "DUTY_CYCLES": 2},  # 50%
    {"PERIOD_CYCLES": 4, "DUTY_CYCLES": 3},  # 75%
    {"PERIOD_CYCLES": 4, "DUTY_CYCLES": 4},  # 100%: always high
    {"PERIOD_CYCLES": 5, "DUTY_CYCLES": 4},  # 80% duty, odd period
    {"PERIOD_CYCLES": 10, "DUTY_CYCLES": 8},  # 80% duty, larger period
]


@pytest.mark.skipif(
    not rtl_exists("pwm_generator.sv"), reason="pwm_generator not implemented yet"
)
@pytest.mark.parametrize(
    "config", CONFIGS, ids=lambda c: f"P{c['PERIOD_CYCLES']}_D{c['DUTY_CYCLES']}"
)
def test_pwm_generator(cocotb_runner, config):
    """Test pwm_generator with various PERIOD_CYCLES and DUTY_CYCLES values."""
    cocotb_runner(
        top="pwm_generator",
        sources=["pwm_generator.sv", "mod_n_counter.sv"],
        test_module="tb_pwm_generator",
        parameters=config,
    )
