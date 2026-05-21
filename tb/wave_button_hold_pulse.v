`timescale 1ns/1ps
module wave_button_hold_pulse;
  reg  clk    = 0;
  reg  button = 0;
  wire pulse;

  button_hold_pulse #(
      .HOLD_CYCLES(5)
  ) dut (
      .clk   (clk),
      .button(button),
      .pulse (pulse)
  );

  always #5 clk = ~clk;

  initial begin
    $dumpfile("wave_button_hold_pulse.vcd");
    $dumpvars(0, wave_button_hold_pulse);

    // Button held long enough: pulse fires exactly once when held asserts,
    // then stays low while button remains held; deasserts when button is released
    #30;
    button = 1;
    #80;
    button = 0;

    // Button released too early: held never asserts, pulse never fires
    #20;
    button = 1;
    #30;
    button = 0;

    // Button held again long enough: pulse fires once more
    #20;
    button = 1;
    #80;
    button = 0;

    #20 $finish;
  end
endmodule
