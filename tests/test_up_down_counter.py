import math

import pytest
from conftest import rtl_exists

# Test configurations: different WIDTH and MAX values
CONFIGS = [
    {"MAX": 9},  # partial range: max < 2^WIDTH - 1
    {"MAX": 7},  # full range:  max == 2^WIDTH - 1
    {"MAX": 200},  # wider counter
]


@pytest.mark.skipif(
    not rtl_exists("up_down_counter.sv"), reason="Up Down Counter not implemented yet"
)
@pytest.mark.parametrize("config", CONFIGS, ids=lambda c: f"M{c['MAX']}")
def test_up_down_counter(cocotb_runner, config):
    """Test up_down_counter with various parameter configurations."""
    config["WIDTH"] = math.ceil(math.log2(config["MAX"]))
    cocotb_runner(
        top="up_down_counter",
        sources=["up_down_counter.sv"],
        test_module="tb_up_down_counter",
        parameters=config,
    )
