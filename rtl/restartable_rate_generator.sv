`timescale 1ns / 1ps

// Restartable rate generator implemented as a Moore FSM.
//
// Parameters:
//   CYCLE_COUNT - number of clock cycles between ticks
//
// Ports:
//   clk     - clock input
//   run     - when high, generator runs and produces ticks
//   tick    - high for one clock cycle every CYCLE_COUNT cycles

module restartable_rate_generator #(
    parameter int CYCLE_COUNT = 1
) (
    input  logic clk,
    input  logic run,
    output logic tick
);

  // Becomes high at the end of each cycle
  logic tick_qualifier;

  logic running = 1'b0;
  always_ff @(posedge clk) running <= run;

  assign tick = running && tick_qualifier;

  generate
    if (CYCLE_COUNT > 1) begin : g_general
      localparam int CountWidth = $clog2(CYCLE_COUNT);

      logic rst_count;
      logic enable_count;
      logic [CountWidth-1:0] count;

      mod_n_counter #(
          .N(CYCLE_COUNT),
          .WIDTH(CountWidth)
      ) u_count (
          .clk   (clk),
          .rst   (rst_count),
          .enable(enable_count),
          .count (count)
      );

      assign rst_count    = !run;
      assign enable_count = run;
      assign tick_qualifier = (count == CountWidth'(CYCLE_COUNT - 1));

    end else begin : g_special
      assign tick_qualifier = 1'b1;
    end
  endgenerate

endmodule
