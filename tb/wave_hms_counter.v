`timescale 1ns / 1ps
module wave_hms_counter;
  reg clk    = 0;
  reg enable = 0;

  // N_SECONDS=5, N_MINUTES=4, N_HOURS=3: full rollover in 60 cycles
  wire [1:0] hours;    // $clog2(3) = 2 bits
  wire [1:0] minutes;  // $clog2(4) = 2 bits
  wire [2:0] seconds;  // $clog2(5) = 3 bits

  hms_counter #(
      .N_HOURS  (3),
      .W_HOURS  (2),
      .N_MINUTES(4),
      .W_MINUTES(2),
      .N_SECONDS(5),
      .W_SECONDS(3)
  ) dut (
      .clk    (clk),
      .enable (enable),
      .hours  (hours),
      .minutes(minutes),
      .seconds(seconds)
  );

  always #5 clk = ~clk;

  initial begin
    $dumpfile("wave_hms_counter.vcd");
    $dumpvars(0, wave_hms_counter);

    // Hold at zero: enable low for two cycles
    #20;

    // Count through one full H:M:S cycle (3 * 4 * 5 = 60 cycles)
    enable = 1;
    #600;

    $finish;
  end
endmodule
