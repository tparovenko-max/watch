`timescale 1ns / 1ps

// Watch V2 - adds mode selection and display flashing
//
// Parameters:
//   CYCLES_PER_SECOND - clock frequency, default 50MHz

module user_top_watch_v2 #(
    parameter int CYCLES_PER_SECOND = 50_000_000
) (
    input  logic       clk,
    /* verilator lint_off UNUSED */
    input  logic [3:0] button,
    input  logic [9:0] sw,
    /* verilator lint_on UNUSED */
    output logic [9:0] led,
    output logic [6:0] hours_disp,
    output logic [6:0] minutes_disp,
    output logic [6:0] seconds_disp,
    output logic       blank_hours,
    output logic       blank_minutes,
    output logic       blank_seconds
);

  // ------------------
  // Core Functionality
  // ------------------

  logic       seconds_tick;
  logic       seconds_edit;
  logic       seconds_inc = '0;
  logic       seconds_dec = '0;
  logic [5:0] seconds;

  editable_counter #(
      .N    (60),
      .WIDTH(6)
  ) u_seconds (
      .clk      (clk),
      .tick     (seconds_tick),
      .edit_mode(seconds_edit),
      .inc      (seconds_inc),
      .dec      (seconds_dec),
      .count    (seconds)
  );

  logic       minutes_tick;
  logic       minutes_edit;
  logic       minutes_inc = '0;
  logic       minutes_dec = '0;
  logic [5:0] minutes;

  editable_counter #(
      .N    (60),
      .WIDTH(6)
  ) u_minutes (
      .clk      (clk),
      .tick     (minutes_tick),
      .edit_mode(minutes_edit),
      .inc      (minutes_inc),
      .dec      (minutes_dec),
      .count    (minutes)
  );

  logic       hours_tick;
  logic       hours_edit;
  logic       hours_inc = '0;
  logic       hours_dec = '0;
  logic [4:0] hours;

  editable_counter #(
      .N    (24),
      .WIDTH(5)
  ) u_hours (
      .clk      (clk),
      .tick     (hours_tick),
      .edit_mode(hours_edit),
      .inc      (hours_inc),
      .dec      (hours_dec),
      .count    (hours)
  );

  // Derive 1 Hz tick from system clock
  restartable_rate_generator #(
      .CYCLE_COUNT(CYCLES_PER_SECOND)
  ) u_divider_1hz (
      .clk (clk),
      .run (1'b1),
      .tick(seconds_tick)
  );

  assign minutes_tick = seconds_tick && (seconds_disp == 7'd59);
  assign hours_tick = minutes_tick && (minutes_disp == 7'd59);

  // Tie edit signals low - no edit in V2
  assign seconds_edit = 1'b0;
  assign minutes_edit = 1'b0;
  assign hours_edit = 1'b0;

  assign hours_disp = {2'b0, hours};
  assign minutes_disp = {1'b0, minutes};
  assign seconds_disp = {1'b0, seconds};

  assign led = 10'b0;

  // --------------
  // Mode Selection
  // --------------

  logic [2:0] mode_enable;

  edit_mode_selector #(
      .HOLD_CYCLES(CYCLES_PER_SECOND)
  ) u_mode_selector (
      .clk        (clk),
      .button     (button[3]),
      .mode_enable(mode_enable)
  );

  // PWM for display flashing - 2Hz, 80% duty cycle
  logic pwm_out;
  pwm_generator #(
      .PERIOD_CYCLES(CYCLES_PER_SECOND / 2),
      .DUTY_CYCLES  (0.8 * CYCLES_PER_SECOND / 2)
  ) u_pwm (
      .clk    (clk),
      .rst    ('0),
      .pwm_out(pwm_out)
  );

  assign blank_seconds = (mode_enable[0]) ? ~pwm_out : '0;
  assign blank_minutes = (mode_enable[1]) ? ~pwm_out : '0;
  assign blank_hours   = (mode_enable[2]) ? ~pwm_out : '0;

endmodule
