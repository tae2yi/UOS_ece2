`timescale 1ns/1ps
// Serial input enters bit 3 and moves toward bit 0.
module shift_register4 (
    input wire clk, rst, enable, serial_in,
    output reg [3:0] value
);

    always @(posedge clk) begin
        if (rst) value <= 4'd0;
        else if (enable) value <= {value[2:0], serial_in};
    end
endmodule
