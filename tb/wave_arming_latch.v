`timescale 1ns/1ps
module wave_arming_latch;
  reg  clk    = 0;
  reg  arm    = 0;
  reg  disarm = 0;
  wire armed;

  arming_latch dut (
      .clk   (clk),
      .arm   (arm),
      .disarm(disarm),
      .armed (armed)
  );

  always #5 clk = ~clk;

  initial begin
    $dumpfile("wave_arming_latch.vcd");
    $dumpvars(0, wave_arming_latch);

    // Arm: armed asserts on next rising edge
    #20;
    arm = 1;
    #10;
    arm = 0;

    // Disarm: armed deasserts on next rising edge
    #30;
    disarm = 1;
    #10;
    disarm = 0;

    // Arm again, then attempt disarm and arm simultaneously: disarm wins
    #20;
    arm = 1;
    #10;
    arm = 0;
    #20;
    arm    = 1;
    disarm = 1;
    #10;
    arm    = 0;
    disarm = 0;

    #20 $finish;
  end
endmodule
