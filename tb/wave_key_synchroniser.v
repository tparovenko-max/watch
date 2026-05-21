`timescale 1ns/1ps
module wave_key_synchroniser;
  reg        clk = 0;
  reg  [3:0] key_n = 4'b1111;  // all released (active-low)
  wire [3:0] key_sync;

  key_synchroniser dut (
      .clk     (clk),
      .key_n   (key_n),
      .key_sync(key_sync)
  );

  always #5 clk = ~clk;

  initial begin
    $dumpfile("wave_key_synchroniser.vcd");
    $dumpvars(0, wave_key_synchroniser);

    // All keys released: key_sync stays 0 after 2 cycles
    #30;

    // Press key[0]: key_sync[0] goes high after 2 cycles
    key_n[0] = 0;
    #30;

    // Release key[0]: key_sync[0] goes low after 2 cycles
    key_n[0] = 1;
    #30;

    // Press key[1]: key_sync[1] goes high after 2 cycles
    key_n[1] = 0;
    #30;

    // Release key[1]
    key_n[1] = 1;
    #30;

    // Press key[2]: key_sync[2] goes high after 2 cycles
    key_n[2] = 0;
    #30;

    // Release key[2]
    key_n[2] = 1;
    #30;

    // Glitch on key[3]: pulse shorter than one clock period
    // (synchroniser captures whatever value is stable at the clock edge)
    key_n[3] = 0;
    #3;  // glitch: shorter than half a period
    key_n[3] = 1;
    #30;

    // Press all four keys simultaneously
    key_n = 4'b0000;
    #30;

    // Release all keys
    key_n = 4'b1111;
    #30;

    $finish;
  end
endmodule
