`timescale 1ns/1ps
module wave_top_time_display_v1;
  reg       clk = 0;
  reg [1:0] SW = 2'b00;
  wire [6:0] HEX5, HEX4, HEX3, HEX2, HEX1, HEX0;

  top_time_display_v1 dut (
      .CLOCK_50(clk),
      .SW      (SW),
      .HEX5    (HEX5),
      .HEX4    (HEX4),
      .HEX3    (HEX3),
      .HEX2    (HEX2),
      .HEX1    (HEX1),
      .HEX0    (HEX0)
  );

  always #10 clk = ~clk;  // 50 MHz: 20 ns period

  initial begin
    $dumpfile("wave_top_time_display_v1.vcd");
    $dumpvars(0, wave_top_time_display_v1);

    // SW=00 (1 Hz): rate divider needs 50M cycles before it ticks;
    // counter holds at 00:00:00 for the entire simulation at this rate
    #80;

    // SW=11 (50 MHz): enable is permanently high, so the counter
    // advances every cycle.  Run for 70 cycles to see seconds roll
    // over from 59 to 0 and minutes increment to 1.
    SW = 2'b11;
    #1400;

    $finish;
  end
endmodule
