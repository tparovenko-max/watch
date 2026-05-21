// To run:
//
//  1. Open a terminal window
//  2. iverilog -Wall -g2012 demos/hello.sv
//  3. ./a.out

module hello;
  initial $display("hello");
endmodule
