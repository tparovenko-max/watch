`timescale 1ns / 1ps
module wave_up_down_counter;
  reg clk = 0;
  reg enable = 0;
  reg up = 1;
  wire [2:0] count;

  up_down_counter #(
      .MAX  (5),
      .WIDTH(3)
  ) dut (
      .clk(clk),
      .enable(enable),
      .up(up),
      .count(count)
  );

  always #5 clk = ~clk;

  initial begin
    $dumpfile("wave_up_down_counter.vcd");
    $dumpvars(0, wave_up_down_counter);

    #20 enable = 1;
    #100 up = 0;
    #100 $finish;
  end
endmodule
