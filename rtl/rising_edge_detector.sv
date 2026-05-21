`timescale 1ns / 1ps

module rising_edge_detector (
    input  logic clk,
    input  logic sig_in,
    output logic rise
);
  //state:was sig_in high on last clock edge
  logic prev = 1'b0;

  //captures sig_in on every rising clock edge
  always_ff @(posedge clk) prev <= sig_in;

  //output depends on both state prev and input sig_in
  assign rise = sig_in && !prev;
endmodule
