`timescale 1ns/1ps
// BDIO0 divided-clock output. A free-running counter at clk (50 MHz)
// supplies the divided bit; for N>=1 the output period is 2^N clocks
// (counter bit [N-1], already a registered signal, 50% duty). For N=0
// the output must reproduce the 50 MHz input clock itself.
//
// The pin is driven through a 7-series ODDR primitive so both halves of
// the output period come from registered data (D1 on the rising edge,
// D2 on the falling edge) instead of a combinational mux on the clock
// pin. DDR_CLK_EDGE="OPPOSITE_EDGE" is used: D1 is captured at the C
// rising edge and drives Q while C is high, D2 is captured at the C
// falling edge and drives Q while C is low. For N=0 we tie D1=1, D2=0,
// so Q simply follows C (the 50 MHz clock). For N>=1 D1=D2=the selected
// divided bit, so Q reproduces that bit with normal ODDR latency.
//
// Icarus has no unisim library, so the testbench supplies its own
// behavioral ODDR model (sim/oddr_sim_model.v) with the same port names;
// Vivado uses the real unisim ODDR for synthesis.
module clk_out_oddr (
    input  wire       clk,
    input  wire [3:0] n_sel,
    output wire        clk_out
);
    reg [8:0] div_counter = 9'd0;

    always @(posedge clk)
        div_counter <= div_counter + 1'b1;

    reg sel_bit;
    always @* begin
        case (n_sel)
            4'd1:    sel_bit = div_counter[0];
            4'd2:    sel_bit = div_counter[1];
            4'd3:    sel_bit = div_counter[2];
            4'd4:    sel_bit = div_counter[3];
            4'd5:    sel_bit = div_counter[4];
            4'd6:    sel_bit = div_counter[5];
            4'd7:    sel_bit = div_counter[6];
            4'd8:    sel_bit = div_counter[7];
            4'd9:    sel_bit = div_counter[8];
            default: sel_bit = 1'b0; // N=0: unused, D1/D2 handle it below
        endcase
    end

    wire d1 = (n_sel == 4'd0) ? 1'b1 : sel_bit;
    wire d2 = (n_sel == 4'd0) ? 1'b0 : sel_bit;

    ODDR #(
        .DDR_CLK_EDGE("OPPOSITE_EDGE"),
        .INIT(1'b0),
        .SRTYPE("SYNC")
    ) u_oddr (
        .Q  (clk_out),
        .C  (clk),
        .CE (1'b1),
        .D1 (d1),
        .D2 (d2),
        .R  (1'b0),
        .S  (1'b0)
    );
endmodule
