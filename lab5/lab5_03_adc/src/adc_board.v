`timescale 1ns/1ps
// 보드용 최상위: 매뉴얼의 adc 모듈을 그대로 쓰고, 보드 핀이 없는 출력
// sample[11:0]·data_valid는 내부에 남긴다(시뮬레이션은 tb가 adc를 직접 검사).
module adc_board(
    input wire clk_50mhz, rst_p,
    input wire [2:0] add_sel,
    output wire adc_sclk, adc_ncs, adc_din,
    input wire adc_dout,
    output wire [7:0] led_out
);
    wire [11:0] sample;
    wire data_valid;
    adc u_adc(clk_50mhz, rst_p, add_sel, adc_sclk, adc_ncs, adc_din,
              adc_dout, sample, data_valid, led_out);
endmodule
