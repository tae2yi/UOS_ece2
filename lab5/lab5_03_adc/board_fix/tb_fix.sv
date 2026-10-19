`timescale 1ns/1ps
// board_fix/serial_frame16.v 검사. ADC 모델은 AD7908처럼 DIN을 SCLK 하강 에지에서 읽는다.
// DOUT은 매뉴얼 TB와 같이 하강 에지에 다음 비트를 내놓는다.
// 채널 1 -> 6을 바꿔 가며 명령 16비트, sample·LED, CS HIGH 시간을 확인한다.
// 시뮬레이션에는 지연이 없어 같은 순간의 변화도 새 값으로 읽히므로, 하강 에지와 같은 시각에
// DIN이 바뀌면 실제 칩에서는 이전 비트를 읽을 수 있는 위반으로 따로 센다.
module tb_fix;
    reg clk=0, rst=1;
    always #5 clk=~clk;
    reg [2:0] channel=1;
    reg miso=0;
    wire sclk,cs_n,mosi,valid;
    wire [11:0] sample;
    wire [7:0] led;
    adc #(.HALF_CYCLES(2)) dut(clk,rst,channel,sclk,cs_n,mosi,miso,sample,valid,led);
    reg [15:0] reply=16'h1A50, cmd=0, seen;
    integer bits=0, bit_no=15, frames=0;
    realtime t_rise=0, gap_min=1e9, t_mosi=-1, t_edge;
    integer din_races=0;
    always @(mosi) t_mosi=$realtime;
    always @(negedge sclk) if(!cs_n) begin
        t_edge=$realtime; #1;
        if(t_mosi==t_edge) din_races=din_races+1;   // 하강 에지와 같은 시각에 DIN 변화
    end
    always @(posedge cs_n) t_rise=$realtime;
    always @(negedge cs_n) begin
        if(t_rise>0 && $realtime-t_rise<gap_min) gap_min=$realtime-t_rise;
        bits=0; bit_no=15; cmd=0;
    end
    always @(negedge sclk) if(!cs_n) begin
        if(bits<16) begin cmd={cmd[14:0],mosi}; bits=bits+1; end   // 하강 에지에서 DIN 읽기
        miso=reply[bit_no]; bit_no=bit_no-1;
    end
    always @(posedge valid) begin
        #1 seen=cmd;
        if(bits!=16) $fatal(1,"bits=%0d",bits);
        if(seen !== (16'hA370 | (channel<<10))) $fatal(1,"ch=%0d cmd=%h",channel,seen);
        if(sample!==reply[11:0] || led!==reply[11:4]) $fatal(1,"sample %h",sample);
        $display("frame %0d: ch=%0d cmd=%h sample=%h led=%h", frames, channel, seen, sample, led);
        frames=frames+1;
        @(negedge clk) channel=6;
    end
    initial begin
        repeat(2) @(negedge clk); rst=0;
        wait(frames==3);
        if(gap_min < 20) $fatal(1,"CS high %0t ns", gap_min);
        if(din_races) $fatal(1,"DIN changed on %0d SCLK falling edges", din_races);
        $display("PASS ADC fix: DIN read on SCLK falling edge, CS high >= %0.0f ns", gap_min);
        $finish;
    end
    initial begin #20000; $fatal(1,"timeout"); end
endmodule
