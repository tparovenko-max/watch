`timescale 1ns / 1ps
//counts up if up == 1, otherwise counts down
// max determined max number it counts up to, width sets bit width-1 in the count
//'0 sets all bits to 0, width'(1) for example sets binary to 1 value with the required bit amounts
//count wraps around from max to 0 for up count, and from 0 to max fro down count


module up_down_counter #(
    parameter int MAX   = 2,
    parameter int WIDTH = 2
) (
    input logic clk,
    input logic enable,
    input logic up,
    output logic [WIDTH-1:0] count
);

  localparam logic [WIDTH-1:0] Max = WIDTH'(MAX);

  initial count = '0;

  logic [WIDTH-1:0] next_count;

  always_comb begin
    if (up) next_count = (count == Max) ? '0 : count + WIDTH'(1);
    else next_count = (count == '0) ? Max : count - WIDTH'(1);
  end

  always_ff @(posedge clk) if (enable) count <= next_count;

endmodule
