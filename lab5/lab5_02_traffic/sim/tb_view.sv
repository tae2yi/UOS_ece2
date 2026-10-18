`timescale 1ns/1ps
// 파형 확인용 TB: CLK_HZ=4라서 4클록(40 ns)이 1초입니다.
// 방향 0의 13단계(초록 0~10초, 노랑 11~12초)와 방향 1의 시작을 보고,
// 이어서 점멸 모드(flicker)를 켭니다. 전수 검사는 tb.sv가 맡습니다.
module tb_view;
    reg clk=0, rst=1, flicker=0;
    always #5 clk=~clk;
    wire [3:0] red,yellow,green,left,walk_red,walk_green;
    traffic #(.CLK_HZ(4)) dut(clk,rst,flicker,red,yellow,green,left,walk_red,walk_green);
    initial begin
        repeat(2) @(negedge clk); rst=0;
        repeat(13*4) @(negedge clk);
        if(dut.direction !== 1 || dut.phase !== 0) $fatal(1,"direction 1 must start");
        if(green !== 4'b0100) $fatal(1,"direction 1 green");
        repeat(8) @(negedge clk);
        flicker=1; repeat(16) @(negedge clk);
        if(red !== 0 || green !== 0) $fatal(1,"flicker outputs");
        flicker=0; repeat(4) @(negedge clk);
        // flicker는 단계만 0으로 돌리고 second_tick은 계속 세므로 그 사이 1초가 지날 수 있습니다.
        if(dut.direction !== 0 || dut.phase > 1) $fatal(1,"flicker must restart sequence");
        $display("PASS traffic view: direction 0 cycle, direction 1 start, flicker");
        $finish;
    end
endmodule
