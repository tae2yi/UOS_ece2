`timescale 1ns/1ps
// 결과보고서용 확인(2026-10-21). 보드 영상에서 LED8(sample[4])이 한 번도 켜지지 않은 원인 확인.
// AD7908의 DOUT처럼 CS 하강 에지에 첫 비트(선행 0)를 내고, 이후 SCLK 하강 에지마다 다음 비트를 낸다.
// 응답 워드: 선행 0, 주소 3비트, 변환값 8비트, 뒤 0 4비트.
// 설계(board_fix/serial_frame16.v)는 SCLK 상승 에지에서 받으므로 한 비트 늦게 받는지 본다.
module tb_dout;
    reg clk=0, rst=1;
    always #5 clk=~clk;
    reg [2:0] channel=1;
    reg miso=0;
    wire sclk,cs_n,mosi,valid;
    wire [11:0] sample;
    wire [7:0] led;
    adc #(.HALF_CYCLES(2)) dut(clk,rst,channel,sclk,cs_n,mosi,miso,sample,valid,led);
    reg [7:0] codes [0:5];
    reg [15:0] reply;
    integer bit_no, frames=0, n_ok=0;
    initial begin
        codes[0]=8'h00; codes[1]=8'h01; codes[2]=8'h55; codes[3]=8'h7F; codes[4]=8'h80; codes[5]=8'hFF;
    end
    always @(negedge cs_n) begin
        reply={1'b0,channel,codes[frames % 6],4'b0000};
        bit_no=15; miso=reply[15];                      // CS 하강: 선행 0
    end
    always @(negedge sclk) if(!cs_n) begin                // SCLK 하강: 다음 비트
        bit_no=bit_no-1;
        miso=(bit_no>=0) ? reply[bit_no] : 1'b0;
    end
    always @(posedge valid) begin
        #1;
        $display("code=%h (%b)  sample=%h  led=%b (%h)  %s", codes[frames % 6], codes[frames % 6], sample, led, led,
                 (led==codes[frames % 6]) ? "same" : "DIFFERENT");
        if(led==codes[frames % 6]) n_ok=n_ok+1;
        frames=frames+1;
    end
    initial begin
        repeat(2) @(negedge clk); rst=0;
        wait(frames==6);
        $display("RESULT %0d of 6 codes shown correctly on LED", n_ok);
        $finish;
    end
    initial begin #40000; $fatal(1,"timeout"); end
endmodule
