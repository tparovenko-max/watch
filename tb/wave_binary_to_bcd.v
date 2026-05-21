`timescale 1ns/1ps
module wave_binary_to_bcd;
  reg  [6:0] bin = 7'd0;
  wire [3:0] tens;
  wire [3:0] ones;

  binary_to_bcd dut (
      .bin (bin),
      .tens(tens),
      .ones(ones)
  );

  initial begin
    $dumpfile("wave_binary_to_bcd.vcd");
    $dumpvars(0, wave_binary_to_bcd);

    // 0: tens=0, ones=0
    bin = 7'd0;
    #20;

    // 9: tens=0, ones=9 (boundary before rollover)
    bin = 7'd9;
    #20;

    // 10: tens=1, ones=0 (first rollover)
    bin = 7'd10;
    #20;

    // 42: tens=4, ones=2 (mid-range)
    bin = 7'd42;
    #20;

    // 99: tens=9, ones=9 (maximum valid input)
    bin = 7'd99;
    #20;

    $finish;
  end
endmodule
