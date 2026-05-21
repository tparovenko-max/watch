import pytest
from conftest import rtl_exists


@pytest.mark.skipif(
    not rtl_exists("mod_n_counter.sv"),
    reason="mod_n_counter not implemented yet",
)
@pytest.mark.parametrize(
    "n,width",
    [
        (5, 3),
        (4, 2),
    ],
)
def test_mod_n_counter(cocotb_runner, n, width):
    """Test mod_n_counter across multiple N/WIDTH parameter pairs."""
    cocotb_runner(
        top="mod_n_counter",
        sources=["mod_n_counter.sv"],
        test_module="tb_mod_n_counter",
        parameters={"N": n, "WIDTH": width},
    )
