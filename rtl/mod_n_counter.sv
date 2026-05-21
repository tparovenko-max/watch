`timescale 1ns / 1ps
module mod_n_counter #(
    parameter int N = 4,
    parameter int WIDTH = 2
) (
    input logic clk,
    input logic rst,
    input logic enable,
    output logic [WIDTH-1:0] count = '0
);
  always_ff @(posedge clk) begin
    if (rst) count <= '0;
    else if (enable) begin
      if (count == WIDTH'(N - 1)) count <= '0;
      else count <= count + 1;
    end
  end
endmodule
