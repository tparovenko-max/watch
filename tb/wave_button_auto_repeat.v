`timescale 1ns/1ps
module wave_button_auto_repeat;
  reg  clk = 0;
  reg  button = 0;
  wire pulse;

  // HOLD_CYCLES=8, REPEAT_CYCLES=3:
  //   hold threshold = HOLD_CYCLES - REPEAT_CYCLES + 1 = 6 cycles
  //   first repeat fires after 6 + 2 = 8 cycles (HOLD_CYCLES)
  //   subsequent repeats every 3 cycles (REPEAT_CYCLES)
  button_auto_repeat #(
      .HOLD_CYCLES  (8),
      .REPEAT_CYCLES(3)
  ) dut (
      .clk   (clk),
      .button(button),
      .pulse (pulse)
  );

  always #5 clk = ~clk;

  initial begin
    $dumpfile("wave_button_auto_repeat.vcd");
    $dumpvars(0, wave_button_auto_repeat);

    // Press and hold long enough: initial pulse on press, then repeats
    #30;
    button = 1;
    #160;
    button = 0;

    // Short press: only the initial pulse fires, no repeats
    #30;
    button = 1;
    #30;
    button = 0;

    // Hold again long enough to confirm repeating behaviour restarts cleanly
    #30;
    button = 1;
    #160;
    button = 0;

    #30 $finish;
  end
endmodule
