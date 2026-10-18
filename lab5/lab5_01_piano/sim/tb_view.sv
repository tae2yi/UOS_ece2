`timescale 1ns/1ps
// 파형 확인용 TB: 도(262 Hz)·미(330 Hz)·높은 도(523 Hz)와 두 키 동시 입력,
// 무입력을 차례로 넣습니다. 전수 검사는 tb.sv가 맡습니다.
// CLK_HZ=10000이므로 반주기는 10000/(2f) 클록: 19, 15, 9클록입니다.
module tb_view;
    reg clk=0, rst=1;
    always #5 clk=~clk;
    reg [7:0] key=0;
    wire piezo;
    piano #(.CLK_HZ(10000)) dut(clk,rst,key,piezo);
    integer edges=0;
    always @(posedge piezo) edges=edges+1;
    initial begin
        repeat(2) @(negedge clk); rst=0;
        @(negedge clk); key=8'h80; repeat(80) @(negedge clk);
        key=8'h20; repeat(64) @(negedge clk);
        key=8'h01; repeat(40) @(negedge clk);
        key=8'hC0; repeat(20) @(negedge clk);
        if(piezo !== 0) $fatal(1,"multiple keys must be silent");
        key=8'h00; repeat(20) @(negedge clk);
        if(piezo !== 0) $fatal(1,"no key must be silent");
        if(edges != 6) $fatal(1,"rising edges=%0d", edges);
        $display("PASS piano view: 262/330/523 Hz tones, %0d rising edges", edges);
        $finish;
    end
endmodule
