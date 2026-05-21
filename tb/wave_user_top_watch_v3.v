`timescale 1ns/1ps
module wave_user_top_watch_v3;
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

  // CYCLES_PER_SECOND=50 keeps the simulation concise:
  //   1 simulated second        = 50 cycles  = 500 ns
  //   PWM period (0.5 s)        = 25 cycles  = 250 ns  (2 Hz flash)
  //   PWM high (0.1 s)          =  5 cycles  =  50 ns  (display off, 20% of period)
  //   Mode-selector hold (1 s)  = 50 cycles  = 500 ns
  //   Auto-repeat hold (0.5 s)  = 25 cycles  = 250 ns
  //   Auto-repeat interval(0.1s)=  5 cycles  =  50 ns
  user_top_watch_v3 #(
      .CYCLES_PER_SECOND(50)
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
    $dumpfile("wave_user_top_watch_v3.vcd");
    $dumpvars(0, wave_user_top_watch_v3);

    // --- Normal operation: watch counts for ~1.5 simulated seconds ---
    // seconds_disp advances once every 50 cycles; all blank_* remain 0.
    #750;  // 75 cycles = 1.5 s

    // --- Long press KEY[3]: enter edit mode, seconds selected ---
    // button_hold_pulse fires after 50 cycles; arming latch sets.
    // mode_enable becomes 3'b001; blank_seconds begins flashing at 2 Hz.
    button[3] = 1;
    #550;  // 55 cycles held (> HOLD_CYCLES=50)
    button[3] = 0;
    #250;  // observe blank_seconds pulsing (1 full PWM period = 250 ns)

    // --- Edit seconds: two single taps of KEY[1] (inc) ---
    // Each rising edge fires one inc_pulse immediately; seconds_disp increments
    // by 1 on each tap.  No auto-repeat because the button is released before
    // the 25-cycle hold threshold.
    button[1] = 1;
    #100;  // 10 cycles (short press)
    button[1] = 0;
    #100;

    button[1] = 1;
    #100;
    button[1] = 0;
    #100;

    // --- Edit seconds: hold KEY[1] to trigger auto-repeat ---
    // First inc_pulse fires on the rising edge (cycle 0 of press).
    // button_hold_detect asserts held at cycle 21 of the press
    // (HOLD_CYCLES - REPEAT_CYCLES + 1 = 25 - 5 + 1 = 21).
    // restartable_rate_generator then fires every 5 cycles while button is held.
    // Holding for 40 cycles produces: 1 (rise) + ~4 (repeat) = 5 pulses.
    button[1] = 1;
    #400;  // 40 cycles held
    button[1] = 0;
    #150;

    // --- Edit seconds: one tap of KEY[0] (dec) ---
    // Rising edge fires one dec_pulse; seconds_disp decrements by 1.
    button[0] = 1;
    #100;
    button[0] = 0;
    #150;

    // --- Short press KEY[3]: cycle from seconds to minutes edit mode ---
    // mod-3 counter in mode_selector advances; mode_enable becomes 3'b010.
    // blank_seconds returns to 0; blank_minutes begins flashing.
    button[3] = 1;
    #100;
    button[3] = 0;
    #250;  // observe blank_minutes pulsing

    // --- Edit minutes: one tap inc, one tap dec ---
    button[1] = 1;
    #100;
    button[1] = 0;
    #100;

    button[0] = 1;
    #100;
    button[0] = 0;
    #150;

    // --- Short press KEY[3]: cycle from minutes to hours edit mode ---
    // mode_enable becomes 3'b100; blank_minutes returns to 0;
    // blank_hours begins flashing.
    button[3] = 1;
    #100;
    button[3] = 0;
    #250;  // observe blank_hours pulsing

    // --- Edit hours: hold KEY[1] for auto-repeat ---
    // Demonstrates auto-repeat on hours; hours_disp increments several times.
    button[1] = 1;
    #400;  // ~5 inc pulses
    button[1] = 0;
    #150;

    // --- Short press KEY[3]: exit edit mode ---
    // disarm condition fires (count == 2 && enable_counter); latch clears.
    // mode_enable returns to 3'b000; all blank_* return to 0.
    button[3] = 1;
    #100;
    button[3] = 0;

    // --- Normal operation resumes ---
    // blank_* all 0; seconds_disp continues incrementing from the clock.
    #500;  // 50 cycles

    $finish;
  end
endmodule
