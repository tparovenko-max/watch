`timescale 1ns/1ps
module wave_decimal_display_driver;
  reg [6:0] value0 = 7'd0;
  reg [6:0] value1 = 7'd0;
  reg [6:0] value2 = 7'd0;
  reg       blank0 = 0;
  reg       blank1 = 0;
  reg       blank2 = 0;

  wire [6:0] HEX0, HEX1, HEX2, HEX3, HEX4, HEX5;

  decimal_display_driver dut (
      .value0(value0),
      .value1(value1),
      .value2(value2),
      .blank0(blank0),
      .blank1(blank1),
      .blank2(blank2),
      .HEX0  (HEX0),
      .HEX1  (HEX1),
      .HEX2  (HEX2),
      .HEX3  (HEX3),
      .HEX4  (HEX4),
      .HEX5  (HEX5)
  );

  initial begin
    $dumpfile("wave_decimal_display_driver.vcd");
    $dumpvars(0, wave_decimal_display_driver);

    // All zeros: HEX1/HEX0 = 00, HEX3/HEX2 = 00, HEX5/HEX4 = 00
    value0 = 7'd0; value1 = 7'd0; value2 = 7'd0;
    blank0 = 0; blank1 = 0; blank2 = 0;
    #20;

    // Distinct values on each pair
    // value0=42 → HEX1='4', HEX0='2'
    // value1=17 → HEX3='1', HEX2='7'
    // value2=99 → HEX5='9', HEX4='9'
    value0 = 7'd42; value1 = 7'd17; value2 = 7'd99;
    #20;

    // Boundary: minimum and maximum on each input
    value0 = 7'd0; value1 = 7'd99; value2 = 7'd50;
    #20;

    // First rollover: tens digit increments at 10
    value0 = 7'd9; value1 = 7'd10; value2 = 7'd11;
    #20;

    // Blanking: blank value1 only; value0 and value2 remain visible
    value0 = 7'd42; value1 = 7'd17; value2 = 7'd99;
    blank1 = 1;
    #20;

    // Blanking: blank0 only; value1 and value2 remain visible
    blank0 = 1; blank1 = 0; blank2 = 0;
    #20;

    // Blanking: blank2 only; value0 and value1 remain visible
    blank0 = 0; blank1 = 0; blank2 = 1;
    #20;

    // Blank all three values
    blank0 = 1; blank1 = 1; blank2 = 1;
    #20;

    // Un-blank: all values reappear
    blank0 = 0; blank1 = 0; blank2 = 0;
    #20;

    $finish;
  end
endmodule
