`timescale 1ns/1ps
// 파형 확인용 TB: UPDATE_CYCLES=4라서 5클록(50 ns)마다 한 번 DAC에 씁니다.
// 처음 8번은 채널 A(a_b=0), 이후 채널 B로 바꿔 4번 더 씁니다.
// 쓰기 LOW 펄스가 끝나는 상승 에지에서 data가 0, 1, 2, ... 순서인지 검사합니다.
module tb_view;
    reg clk=0,rst=1,channel=0;
    always #5 clk=~clk;
    wire cs_n,ldac_n,we_n,a_b;
    wire [7:0] data,led;
    dac #(.UPDATE_CYCLES(4)) dut(clk,rst,channel,cs_n,ldac_n,we_n,a_b,data,led);
    integer writes=0;
    always @(posedge we_n) if(!rst) begin
        if(data !== writes || a_b !== (writes>=8)) $fatal(1,"write %0d data %0d a_b %b",writes,data,a_b);
        writes=writes+1;
    end
    initial begin
        repeat(2) @(negedge clk); rst=0;
        wait(writes==8); @(negedge clk); channel=1;
        wait(writes==12); repeat(3) @(negedge clk);
        $display("PASS DAC view: 12 writes (0..11), channel A then B");
        $finish;
    end
endmodule
