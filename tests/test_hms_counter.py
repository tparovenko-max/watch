import math

import pytest
from conftest import rtl_exists

# Small parameters keep simulation fast while still exercising all rollover paths.
# The power-of-2 config is specifically chosen so that $clog2(N) != $clog2(N-1)
# for each parameter (e.g. $clog2(2)=1 but $clog2(1)=0), which catches any
# off-by-one error in port-width calculation.
CONFIGS = [
    {
        "N_HOURS": 2,
        "N_MINUTES": 2,
        "N_SECONDS": 2,
    },  # powers of 2: catches N-1 width bug
    {"N_HOURS": 3, "N_MINUTES": 4, "N_SECONDS": 5},
    {"N_HOURS": 24, "N_MINUTES": 60, "N_SECONDS": 60},
]


@pytest.mark.skipif(
    not rtl_exists("hms_counter.sv"), reason="hms_counter module not implemented yet"
)
@pytest.mark.parametrize(
    "config",
    CONFIGS,
    ids=lambda c: f"H{c['N_HOURS']}_M{c['N_MINUTES']}_S{c['N_SECONDS']}",
)
def test_hms_counter(cocotb_runner, config):
    """Test hms_counter seconds/minutes/hours cascade for various configurations."""
    config["W_HOURS"] = math.ceil(math.log2(config["N_HOURS"]))
    config["W_MINUTES"] = math.ceil(math.log2(config["N_MINUTES"]))
    config["W_SECONDS"] = math.ceil(math.log2(config["N_SECONDS"]))
    cocotb_runner(
        top="hms_counter",
        sources=["up_down_counter.sv", "hms_counter.sv"],
        test_module="tb_hms_counter",
        parameters=config,
    )
