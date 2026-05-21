## Manual Testbenches

These testbenches are a starting point for manual simulation and waveform inspection. You may still need to write additional testbenches to cover edge cases or isolate bugs.

A consistent naming convention is used. For example, to run the testbench for `arming_latch`, from the project root (`/workspace`) run:
```
iverilog -Wall -g2012 -Y .sv -y rtl tb/wave_arming_latch.v
./a.out
```

This generates `wave_arming_latch.vcd`. To open it in VaporView in VS Code, either click the file in the Explorer pane or use **File > Open File...** and select it. You can also open it with any waveform viewer installed on your host machine.
