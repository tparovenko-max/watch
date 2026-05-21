`timescale 1ns / 1ps

// PWM generator with fixed frequency and duty cycle.
//
// Parameters:
//   PERIOD_CYCLES - number of clock cycles in one PWM period
//   DUTY_CYCLES   - number of clock cycles output is high
//
// Ports:
//   clk     - clock input
//   rst     - when high, restarts the PWM period
//   pwm_out - PWM output signal
module pwm_generator #(
    //NUmber of clock cycles in one PWM period
    parameter int PERIOD_CYCLES = 50_000_000,
    // number of clock cycles output is high
    parameter int DUTY_CYCLES   = 25_000_000
) (
    input  logic clk,
    input  logic rst,
    output logic pwm_out
);

  localparam int CountWidth = $clog2(PERIOD_CYCLES + 1);

  logic [CountWidth-1:0] count;

  mod_n_counter #(
      .N    (PERIOD_CYCLES),
      .WIDTH(CountWidth)
  ) u_counter (
      .clk   (clk),
      .rst   (rst),
      .enable(1'b1),
      .count (count)
  );

  assign pwm_out = (count < DUTY_CYCLES);

endmodule
