`timescale 1ns/1ps
module wave_user_top_watch_v1;
  reg        clk    = 0;
  reg  [3:0] button = 4'b0;
  reg  [9:0] sw     = 10'b0;
  wire [9:0] led;
  wire [6:0] hours_disp;
  wire [6:0] minutes_disp;
  wire [6:0] seconds_disp;
  wire       blank_hours;
  wire       blank_minutes;
  wire       blank_seconds;

  // Override CYCLES_PER_SECOND so each simulated second is 10 clock cycles.
  // seconds_tick fires every 100 ns; one simulated minute takes 6000 ns.
  user_top_watch_v1 #(
      .CYCLES_PER_SECOND(10)
  ) dut (
      .clk         (clk),
      .button      (button),
      .sw          (sw),
      .led         (led),
      .hours_disp  (hours_disp),
      .minutes_disp(minutes_disp),
      .seconds_disp(seconds_disp),
      .blank_hours  (blank_hours),
      .blank_minutes(blank_minutes),
      .blank_seconds(blank_seconds)
  );

  always #5 clk = ~clk;  // 100 MHz: 10 ns period

  initial begin
    $dumpfile("wave_user_top_watch_v1.vcd");
    $dumpvars(0, wave_user_top_watch_v1);

    // Run for 2 minutes and 5 seconds of simulated time.
    // This shows: seconds counting 0..59 and wrapping twice,
    // minutes_tick firing at t=60 s and t=120 s, and minutes
    // advancing from 0 to 2.  hours_tick does not fire (would
    // require 60 full minutes).
    // 125 s x 10 cycles/s x 10 ns/cycle = 12500 ns
    #12500;

    $finish;
  end
endmodule
