`timescale 1ns/1ps
// Convert a 17-bit unsigned millisecond count (0..99999) into five packed
// BCD digits using the double-dabble algorithm. Adapted from
// exercise/week3/src/binary_to_bcd8.v, narrowed from 8 digits/27 bits to
// 5 digits/17 bits to match this project's 5-digit LCD readout.
module binary_to_bcd5 (
    input  wire [16:0] binary_value,
    output reg  [19:0] bcd_digits
);
    function [19:0] convert_to_bcd;
        input [16:0] value;
        integer bit_index;
        integer digit_index;
        reg [19:0] work;
        begin
            work = 20'd0;
            for (bit_index = 16; bit_index >= 0; bit_index = bit_index - 1) begin
                for (digit_index = 0; digit_index < 5; digit_index = digit_index + 1) begin
                    if (work[digit_index*4 +: 4] >= 4'd5)
                        work[digit_index*4 +: 4] =
                            work[digit_index*4 +: 4] + 4'd3;
                end
                work = {work[18:0], value[bit_index]};
            end
            convert_to_bcd = work;
        end
    endfunction

    always @* begin
        bcd_digits = convert_to_bcd(binary_value);
    end
endmodule
