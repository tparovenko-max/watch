import pytest
from conftest import rtl_exists


@pytest.mark.skipif(
    not rtl_exists("editable_counter.sv"),
    reason="editable_counter not implemented yet",
)
@pytest.mark.parametrize(
    "n,width",
    [
        (5, 3),
        (4, 2),
        (60, 6),
    ],
)
def test_editable_counter(cocotb_runner, n, width):
    """Test editable_counter for various N/WIDTH combinations."""
    cocotb_runner(
        top="editable_counter",
        sources=["up_down_counter.sv", "editable_counter.sv"],
        test_module="tb_editable_counter",
        parameters={"N": n, "WIDTH": width},
    )
