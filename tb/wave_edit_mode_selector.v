`timescale 1ns/1ps
module wave_edit_mode_selector;
  reg        clk    = 0;
  reg        button = 0;
  wire [2:0] mode_enable;

  // HOLD_CYCLES=5: button must be held for 5 consecutive rising edges for
  // long_press to fire.  armed asserts one cycle later (rising-edge detector
  // pipeline), so mode_enable becomes non-zero ~6 cycles after button goes high.
  edit_mode_selector #(
      .HOLD_CYCLES(5)
  ) dut (
      .clk        (clk),
      .button     (button),
      .mode_enable(mode_enable)
  );

  always #5 clk = ~clk;

  initial begin
    $dumpfile("wave_edit_mode_selector.vcd");
    $dumpvars(0, wave_edit_mode_selector);

    // Long press: hold for 10 cycles to ensure long_press fires and armed asserts.
    // mode_enable -> 3'b001 (mode 0)
    #30;
    button = 1;
    #100;
    button = 0;

    // Short press 1: count advances 0->1, mode_enable -> 3'b010 (mode 1)
    #30;
    button = 1;
    #20;
    button = 0;

    // Short press 2: count advances 1->2, mode_enable -> 3'b100 (mode 2)
    #30;
    button = 1;
    #20;
    button = 0;

    // Short press 3: count==2 and press fires disarm; armed clears,
    // mode_enable -> 3'b000
    #30;
    button = 1;
    #20;
    button = 0;

    // Short presses while disarmed: mode_enable stays 3'b000
    #30;
    button = 1;
    #20;
    button = 0;
    #30;
    button = 1;
    #20;
    button = 0;

    // Second long press: armed asserts again, mode_enable -> 3'b001
    #50;
    button = 1;
    #100;
    button = 0;

    #50 $finish;
  end
endmodule
