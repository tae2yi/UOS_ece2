`timescale 1ns/1ps
// 보드 확인용 수정본(src/serial_frame16.v와 포트·동작 순서는 같다).
// 증상: 보드에서 DIP_SW1로 채널을 바꿔도 ADC 값이 바뀌지 않음(2026-10-19).
// AD7908은 DIN을 SCLK 하강 에지에서 읽는다. 원본은 같은 하강 에지에 다음 비트를 내보내
// 칩이 이전 비트를 한 번 더 읽을 수 있으므로, 다음 비트를 상승 에지(수신과 같은 때)에 바꾼다.
// 또 프레임 사이 CS HIGH 시간이 2클록(40 ns)뿐이라, 다음 시작 전 HALF_CYCLES 클록을 쉰다.
module serial_frame16 #(parameter HALF_CYCLES=25)(
    input wire clk_50mhz,rst_p,start,
    input wire [15:0] tx_word,
    input wire miso,
    output reg sclk,cs_n,mosi,busy,done,
    output reg [15:0] rx_word
);
    reg [31:0] count, idle;
    reg [4:0] bit_index;
    reg [15:0] tx_latched;
    always @(posedge clk_50mhz) begin
        if(rst_p) begin
            sclk<=1; cs_n<=1; mosi<=0; busy<=0; done<=0; idle<=0;
            count<=0; bit_index<=15; tx_latched<=0; rx_word<=0;
        end else begin
            done<=0;
            if(!busy) begin
                if(idle < HALF_CYCLES) idle<=idle+1;
                else if(start) begin
                    cs_n<=0; busy<=1; count<=0; bit_index<=15;
                    tx_latched<=tx_word; rx_word<=0; mosi<=tx_word[15];
                end
            end else if(count==HALF_CYCLES-1) begin
                count<=0;
                if(sclk) sclk<=0;                 // 칩이 이 하강 에지에서 DIN을 읽음
                else begin
                    sclk<=1;
                    rx_word<={rx_word[14:0],miso};
                    if(bit_index==0) begin
                        busy<=0; cs_n<=1; done<=1; idle<=0;
                    end else begin
                        bit_index<=bit_index-1'b1;
                        mosi<=tx_latched[bit_index-1'b1];
                    end
                end
            end else count<=count+1;
        end
    end
endmodule
