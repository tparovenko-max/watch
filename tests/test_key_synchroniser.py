import pytest
from conftest import rtl_exists


@pytest.mark.skipif(
    not rtl_exists("key_synchroniser.sv"),
    reason="key_synchroniser not implemented yet",
)
def test_key_sync(cocotb_runner):
    """Test key_sync synchronisation, inversion, and 2-cycle latency."""
    cocotb_runner(
        top="key_synchroniser",
        sources=["key_synchroniser.sv"],
        test_module="tb_key_synchroniser",
    )
