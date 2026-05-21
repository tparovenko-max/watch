`timescale 1ns/1ps
module wave_seven_segment;
  reg  [3:0] digit = 4'h0;
  reg        blank = 0;
  wire [6:0] segments;

  seven_segment dut (
      .digit   (digit),
      .blank   (blank),
      .segments(segments)
  );

  initial begin
    $dumpfile("wave_seven_segment.vcd");
    $dumpvars(0, wave_seven_segment);

    // Digit 1 (b,c only): blank low shows two segments
    digit = 4'h1;
    blank = 0;
    #20;
    // Blank high: all segments off regardless of digit
    blank = 1;
    #20;

    // Digit 5 (a,c,d,f,g): blank low shows five segments
    digit = 4'h5;
    blank = 0;
    #20;
    // Blank high: all segments off
    blank = 1;
    #20;

    // Digit 8 (all segments): blank low shows all seven segments
    digit = 4'h8;
    blank = 0;
    #20;
    // Blank high: all segments off
    blank = 1;
    #20;

    $finish;
  end
endmodule
