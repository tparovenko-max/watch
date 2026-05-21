// takes in a bin value and splits it into 2 four bit numbers representing decimal ones and tens, using division and modulo



`timescale 1ns / 1ps
module binary_to_bcd (
    input  logic [6:0] bin,   // binary input, 0-99
    output logic [3:0] tens,  //decimal tens digit (BCD)
    output logic [3:0] ones   //decimal ones digit (BCD)
);
  assign tens = 4'(bin / 7'd10);
  assign ones = 4'(bin % 7'd10);

endmodule
