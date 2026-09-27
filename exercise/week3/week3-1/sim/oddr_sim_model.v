`timescale 1ns/1ps
// Sim-only behavioral model of the 7-series ODDR primitive, DDR_CLK_EDGE
// = "OPPOSITE_EDGE" behavior only (that is all src/clk_out_oddr.v uses).
// D1 is registered on the C rising edge and drives Q while C is high;
// D2 is registered on the C falling edge and drives Q while C is low.
// Icarus has no unisim library, so this module (same name/ports as the
// real primitive) stands in for it during simulation; Vivado uses the
// real ODDR for synthesis and never sees this file.
module ODDR #(
    parameter DDR_CLK_EDGE = "OPPOSITE_EDGE",
    parameter INIT         = 1'b0,
    parameter SRTYPE       = "SYNC"
) (
    output reg  Q,
    input  wire C,
    input  wire CE,
    input  wire D1,
    input  wire D2,
    input  wire R,
    input  wire S
);
    reg d1_reg = INIT;
    reg d2_reg = INIT;

    always @(posedge C) begin
        if (R)
            d1_reg <= 1'b0;
        else if (S)
            d1_reg <= 1'b1;
        else if (CE)
            d1_reg <= D1;
    end

    always @(negedge C) begin
        if (R)
            d2_reg <= 1'b0;
        else if (S)
            d2_reg <= 1'b1;
        else if (CE)
            d2_reg <= D2;
    end

    always @* Q = C ? d1_reg : d2_reg;
endmodule
