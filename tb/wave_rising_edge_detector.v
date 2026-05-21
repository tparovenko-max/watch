`timescale 1ns / 1ps
module wave_rising_edge_detector;
  reg  clk = 0;
  reg  sig_in = 0;
  wire rise;

  rising_edge_detector dut (
      .clk   (clk),
      .sig_in(sig_in),
      .rise  (rise)
  );

  always #5 clk = ~clk;

  initial begin
    $dumpfile("wave_rising_edge_detector.vcd");
    $dumpvars(0, wave_rising_edge_detector);

    // sig_in low: rise stays low
    #30;
    // First rising edge: rise asserts for one cycle then deasserts
    sig_in = 1;
    #30;
    // sig_in falls: rise stays low (no assertion on falling edge)
    sig_in = 0;
    #20;

    // Second rising edge: rise asserts again for one cycle
    sig_in = 1;
    #20;
    sig_in = 0;
    #20;

    // --- Misaligned pulse: starts at t=120ns, not aligned with negedge clk ---
    #3;  // t=123ns, clk is not at an edge
    sig_in = 1;
    #7;  // t=130ns, clk will have a negedge at t=125, 135, etc.
    sig_in = 0;
    #10;

    // --- Very short pulse: too short to be seen at any rising clk edge ---
    #2;  // t=142ns
    sig_in = 1;
    #2;  // t=144ns
    sig_in = 0;
    #14;

    $finish;
  end
endmodule
