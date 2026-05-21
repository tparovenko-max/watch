import pytest
from conftest import rtl_exists

CONFIGS = [
    {"CYCLE_COUNT": 1},  # edge case: tick permanently high
    {"CYCLE_COUNT": 3},  # one below a power of 2 (4-1); tests clog2 boundary
    {"CYCLE_COUNT": 4},  # exact power of 2; counter is exactly full-width
    {"CYCLE_COUNT": 5},  # one above a power of 2 (4+1); tests clog2 boundary
    {"CYCLE_COUNT": 8},  # power of two; used by button_auto_repeat tests
    {"CYCLE_COUNT": 100},  # larger value; verifies clog2 gives a 7-bit counter
]


@pytest.mark.skipif(
    not rtl_exists("restartable_rate_generator.sv"),
    reason="restartable_rate_generator not implemented yet",
)
@pytest.mark.parametrize("config", CONFIGS, ids=lambda c: f"C{c['CYCLE_COUNT']}")
def test_restartable_rate_generator(cocotb_runner, config):
    """Test restartable_rate_generator with various CYCLE_COUNT values."""
    cocotb_runner(
        top="restartable_rate_generator",
        sources=["restartable_rate_generator.sv", "mod_n_counter.sv"],
        test_module="tb_restartable_rate_generator",
        parameters=config,
    )
