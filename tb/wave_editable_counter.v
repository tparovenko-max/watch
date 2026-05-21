`timescale 1ns / 1ps
module wave_editable_counter;
  reg        clk = 0;
  reg        tick = 0;
  reg        edit_mode = 0;
  reg        inc = 0;
  reg        dec = 0;
  wire [1:0] count;

  editable_counter #(
      .N(3),
      .WIDTH(2)
  ) dut (
      .clk      (clk),
      .tick     (tick),
      .edit_mode(edit_mode),
      .inc      (inc),
      .dec      (dec),
      .count    (count)
  );


  always #5 clk = ~clk;

  // Tick pulses at a constant rate (every 30ns, 10ns high, 20ns low)
  always begin
    #20;
    tick = 1;
    #10;
    tick = 0;
  end

  initial begin
    $dumpfile("wave_editable_counter.vcd");
    $dumpvars(0, wave_editable_counter);

    // Start in tick mode: count increments on each tick
    #10;
    // Let a few ticks increment the counter
    #120;

    // Edit mode: tick pulses continue, but are ignored
    edit_mode = 1;
    inc = 1;
    // Only inc controls the counter now; tick pulses have no effect
    #60;
    inc = 0;

    // Edit mode: count down
    #10;
    dec = 1;
    #60;
    dec = 0;

    // Both inc and dec asserted: count holds (enable is gated off)
    #10;
    inc = 1;
    dec = 1;
    #40;
    inc = 0;
    dec = 0;

    // Return to tick mode: counting resumes on tick
    #20;
    edit_mode = 0;
    #120;

    #20;
    $finish;
  end
endmodule
