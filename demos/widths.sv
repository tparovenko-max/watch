// To run:
//
//  1. Open a terminal window
//  2. iverilog -Wall -g2012 demos/widths.sv
//  3. ./a.out

module widths;
  logic [3:0] x;

  initial begin
    x = '0;
    $display(x, " '0");
    x = '1;
    $display(x, " '1");
  end
endmodule
