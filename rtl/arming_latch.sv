`timescale 1ns / 1ps

// Arming latch - a flip-flop with synchronous set and clear.
//
// Ports:
//   clk    - clock input
//   arm    - when high, sets armed
//   disarm - when high, clears armed (takes priority over arm)
//   armed  - output, high when armed

module arming_latch (
    input  logic clk,
    input  logic arm,
    input  logic disarm,
    output logic armed
);

initial armed = 1'b0;

  always_ff @(posedge clk) begin
    if (disarm) armed <= 1'b0;
    else if (arm) armed <= 1'b1;
  end

endmodule
