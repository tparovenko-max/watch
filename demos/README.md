## Demonstrations

This folder contains small examples to verify your toolchain and get familiar
with simulation commands.

## Prerequisites

- Open this repository in the dev container.
- Run commands from the repository root.

## Demos

### Hello

Minimal SystemVerilog compile and run test.

```sh
iverilog -Wall -g2012 demos/hello.sv
./a.out
```

Expected output:

```text
hello
```

### Simulation

Shows how language mode changes simulator behaviour.

Run as Verilog:

```sh
iverilog -Wall demos/simulation.v
./a.out
```

Run as SystemVerilog:

```sh
iverilog -Wall -g2012 demos/simulation.v
./a.out
```

The testbench also writes `simulation.vcd`, which you can inspect in a waveform
viewer.

### Widths

Demonstrates how the literals `'0` and `'1` expand when
assigned to a fixed-width signal.

```sh
iverilog -Wall -g2012 demos/widths.sv
./a.out
```

## Notes

- `a.out` is overwritten each time you compile with `iverilog` unless you pass
	`-o <name>`.
- Remember to add the `-g2012` directive to `iverilog` whenever compiling a SystemvVerilog file (one with an `.sv` extension).
