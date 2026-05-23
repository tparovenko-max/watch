`timescale 1ns / 1ps

// Watch V1 - basic timekeeping
//
// Parameters:
//   CYCLES_PER_SECOND - clock frequency, default 50MHz
//
// Ports:
//   clk            - clock input
//   button         - synchronised active-high button inputs
//   sw             - switch inputs (unused)
//   led            - LED outputs (unused)
//   hours_disp     - hours value for display (0-23)
//   minutes_disp   - minutes value for display (0-59)
//   seconds_disp   - seconds value for display (0-59)
//   blank_hours    - blanking control for hours display
//   blank_minutes  - blanking control for minutes display
//   blank_seconds  - blanking control for seconds display

module user_top_watch_v1 #(
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

  // Seconds
  logic       seconds_tick;
  logic       seconds_edit;
  logic       seconds_inc;
  logic       seconds_dec;
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

  // Minutes
  logic       minutes_tick;
  logic       minutes_edit;
  logic       minutes_inc;
  logic       minutes_dec;
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

  // Hours
  logic       hours_tick;
  logic       hours_edit;
  logic       hours_inc;
  logic       hours_dec;
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

  // Minutes ticks when seconds rolls over
  assign minutes_tick  = seconds_tick && (seconds == 6'b111011);

  // Hours ticks when minutes rolls over
  assign hours_tick    = minutes_tick && (minutes == 6'b111011);

  // Tie edit signals low - no edit in V1
  assign seconds_edit  = 1'b0;
  assign minutes_edit  = 1'b0;
  assign hours_edit    = 1'b0;

  assign seconds_inc   = 1'b0;
  assign seconds_dec   = 1'b0;
  assign minutes_inc   = 1'b0;
  assign minutes_dec   = 1'b0;
  assign hours_inc     = 1'b0;
  assign hours_dec     = 1'b0;

  // Zero-extend counter values to display outputs
  assign hours_disp    = {2'b0, hours};
  assign minutes_disp  = {1'b0, minutes};
  assign seconds_disp  = {1'b0, seconds};

  // Unused outputs
  assign led           = 10'b0;
  assign blank_hours   = 1'b0;
  assign blank_minutes = 1'b0;
  assign blank_seconds = 1'b0;

endmodule
