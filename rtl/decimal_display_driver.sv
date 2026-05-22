`timescale 1ns / 1ps

// Decimal display driver for the DE1-SoC HEX displays.
//
// Parameters:
//   None
//
// Ports:
//   value0 [6:0] - Decimal value to display on HEX1 (tens) and HEX0 (ones).
//   value1 [6:0] - Decimal value to display on HEX3 (tens) and HEX2 (ones).
//   value2 [6:0] - Decimal value to display on HEX5 (tens) and HEX4 (ones).
//   blank0       - When high, blanks both digits of value0.
//   blank1       - When high, blanks both digits of value1.
//   blank2       - When high, blanks both digits of value2.
//   HEX0..5 [6:0] - Active-low seven-segment display outputs.

module decimal_display_driver (
    input logic [6:0] value0,
    input logic [6:0] value1,
    input logic [6:0] value2,

    input logic blank0,
    input logic blank1,
    input logic blank2,

    output logic [6:0] HEX0,
    output logic [6:0] HEX1,
    output logic [6:0] HEX2,
    output logic [6:0] HEX3,
    output logic [6:0] HEX4,
    output logic [6:0] HEX5
);

  // Pack scalar ports into arrays for use in the generate loop.
  // value_a[i] drives HEX(2i+1) (tens) and HEX(2i) (ones).
  logic [6:0] value_a[3];
  assign value_a[0] = value0;
  assign value_a[1] = value1;
  assign value_a[2] = value2;

  logic blank_a[3];
  assign blank_a[0] = blank0;
  assign blank_a[1] = blank1;
  assign blank_a[2] = blank2;

  logic [6:0] hex_a[6];
  assign HEX0 = hex_a[0];
  assign HEX1 = hex_a[1];
  assign HEX2 = hex_a[2];
  assign HEX3 = hex_a[3];
  assign HEX4 = hex_a[4];
  assign HEX5 = hex_a[5];

  genvar i;
  generate
    for (i = 0; i < 3; i = i + 1) begin : g_digit_pair
      logic [3:0] tens;
      logic [3:0] ones;

      binary_to_bcd u_bcd (
          .bin (value_a[i]),
          .tens(tens),
          .ones(ones)
      );

      seven_segment u_seg_tens (
          .digit   (tens),
          .blank   (blank_a[i]),
          .segments(hex_a[2*i+1])
      );

      seven_segment u_seg_ones (
          .digit   (ones),
          .blank   (blank_a[i]),
          .segments(hex_a[2*i])
      );
    end
  endgenerate

endmodule
