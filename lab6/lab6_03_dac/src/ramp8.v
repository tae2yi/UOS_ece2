`timescale 1ns/1ps
module ramp8 #(parameter UPDATE_CYCLES=500_000)(
    input wire clk_50mhz,rst_p,
    output reg [7:0] value,
    output wire update
);
    reg [31:0] count;
    assign update=(count==UPDATE_CYCLES-1);
    always @(posedge clk_50mhz) begin
        if(rst_p) begin count<=0; value<=0; end
        else if(update) begin count<=0; value<=value+1'b1; end
        else count<=count+1;
    end
endmodule
