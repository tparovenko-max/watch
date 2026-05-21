import pytest
from conftest import rtl_exists

# Test both active-low (DE1-SoC default) and active-high configurations
CONFIGS = [
    {"ACTIVE_LOW": 1},
    {"ACTIVE_LOW": 0},
]


@pytest.mark.skipif(
    not rtl_exists("seven_segment.sv"), reason="Seven-segment module not implemented yet"
)
@pytest.mark.parametrize("config", CONFIGS, ids=lambda c: f"AL{c['ACTIVE_LOW']}")
def test_seven_segment(cocotb_runner, config):
    """Test seven_segment decoder for all hex digits and blank input."""
    cocotb_runner(
        top="seven_segment",
        sources=["seven_segment.sv"],
        test_module="tb_seven_segment",
        parameters=config,
    )
