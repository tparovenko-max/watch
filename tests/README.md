
## Automated Tests

This directory contains automated tests to verify your hardware design.

- Tests are executed using `pytest`.
- If all tests pass, your design is very likely functionally correct.
- Comments within the test files explain what is being checked.

**Example:**
For the module `arming_latch`, the corresponding test is `tests/test_arming_latch.py`. This test first checks if `rtl/arming_latch.sv` exists. If not, the test is skipped. If it does exist, `tests/cocotb/tb_arming_latch.py` is run to perform the simulation-based checks.

The tests are written in Python using the `cocotb` library, enabling real-time interaction between Python testbenches and your Verilog code during simulation. This is accomplished by embedding a Python interpreter within the `iverilog` simulator.
