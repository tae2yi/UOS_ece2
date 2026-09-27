`timescale 1ns/1ps
// Eight-digit 7-segment scanner, adapted from week3's seg7_scan8. At
// 50 MHz a scan-tick prescaler advances one digit roughly every
// SCAN_TICK_CYCLES clocks (~1 kHz per digit at the default), giving a
// steady full-frame refresh. Segment outputs are active-high, the
// board's digit common pins are active-low. Digit code 4'hF is blank
// (all segments off); this falls through the decode case's default, so
// it needs no special-case handling. No decimal point is driven.
module seg7_scan8 #(
    parameter integer SCAN_TICK_CYCLES = 50_000
) (
    input  wire        clk,
    input  wire [31:0] digit_codes,
    output reg  [7:0]  seg_data,
    output wire [7:0]  seg_com,
    output reg  [2:0]  digit_index = 3'd0
);
    localparam integer PRESCALE_W = $clog2(SCAN_TICK_CYCLES + 1);
    reg [PRESCALE_W-1:0] presc = {PRESCALE_W{1'b0}};
    wire tick = (presc == SCAN_TICK_CYCLES - 1);

    always @(posedge clk)
        presc <= tick ? {PRESCALE_W{1'b0}} : presc + 1'b1;

    always @(posedge clk)
        if (tick)
            digit_index <= digit_index + 1'b1;

    reg [3:0] digit;
    reg [7:0] selected;

    always @* begin
        digit    = digit_codes >> (digit_index * 4);
        selected = 8'b0000_0001 << digit_index;
        case (digit)
            4'd0: seg_data = 8'b11111100;
            4'd1: seg_data = 8'b01100000;
            4'd2: seg_data = 8'b11011010;
            4'd3: seg_data = 8'b11110010;
            4'd4: seg_data = 8'b01100110;
            4'd5: seg_data = 8'b10110110;
            4'd6: seg_data = 8'b10111110;
            4'd7: seg_data = 8'b11100000;
            4'd8: seg_data = 8'b11111110;
            4'd9: seg_data = 8'b11110110;
            default: seg_data = 8'b00000000; // includes blank code 4'hF
        endcase
    end

    // On this board COM[7] is the leftmost digit and COM[0] is the
    // rightmost; digit_codes nibble 0 is the rightmost display position.
    assign seg_com = ~selected;
endmodule
