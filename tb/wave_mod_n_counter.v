`timescale 1ns / 1ps
module wave_mod_n_counter;
  reg        clk = 0;
  reg        rst = 0;
  reg        enable = 0;
  wire [2:0] count;

  mod_n_counter #(
      .N(5),
      .WIDTH(3)
  ) dut (
      .clk   (clk),
      .rst   (rst),
      .enable(enable),
      .count (count)
  );

  always #5 clk = ~clk;

  initial begin
    $dumpfile("wave_mod_n_counter.vcd");
    $dumpvars(0, wave_mod_n_counter);

    // Reset: count stays at 0
    rst = 1;
    #30;
    rst = 0;

    // Count through a full cycle (0 to 4, then wrap to 0)
    enable = 1;
    #110;

    // Enable gated low: count holds
    enable = 0;
    #30;
    enable = 1;

    // Reset mid-count: count returns to 0 immediately
    #40;
    rst = 1;
    #10;
    rst = 0;

    // Count through another full cycle to confirm recovery
    #110;

    #20 $finish;
  end
endmodule
