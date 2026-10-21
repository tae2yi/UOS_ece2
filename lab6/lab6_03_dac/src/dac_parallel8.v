`timescale 1ns/1ps
// 데이터는 쓰기 LOW 펄스 전에 등록하고, 펄스 종료까지 유지합니다.
module dac_parallel8(
    input wire clk_50mhz,rst_p,update,channel,
    input wire [7:0] value,
    output wire cs_n,ldac_n,
    output reg we_n,a_b,
    output reg [7:0] data
);
    assign cs_n=0;
    assign ldac_n=0;
    always @(posedge clk_50mhz) begin
        if(rst_p) begin we_n<=1; a_b<=0; data<=0; end
        else begin
            we_n<=1;
            if(update) begin data<=value; a_b<=channel; we_n<=0; end
        end
    end
endmodule
