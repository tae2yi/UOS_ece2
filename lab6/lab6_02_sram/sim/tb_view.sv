`timescale 1ns/1ps
// 파형 확인용 TB: 주소 0~3에 값 9, 6, A, 3을 쓰고 같은 주소를 다시 읽습니다.
// 단계마다 20 ns를 두어 버스 방향(쓰기: FPGA 구동, 읽기·대기: Z)이 보이게 합니다.
// 마지막에 쓰기·읽기를 함께 요청해 둘 다 무시되는지 봅니다.
module sram_model(
    input wire cs_n,oe_n,we_n,
    input wire [17:0] address,
    inout wire [15:0] data
);
    reg [15:0] memory[0:15];
    assign data=(!cs_n && !oe_n && we_n) ? memory[address[3:0]] : 16'bz;
    always @(negedge we_n) begin
        #1;
        if(!cs_n && !we_n) memory[address[3:0]]=data;
    end
endmodule

module tb_view;
    reg wr=0,rd=0;
    reg [3:0] address=0,data_in=0;
    wire cs_n,oe_n,we_n;
    wire [17:0] ram_address;
    wire [15:0] bus;
    wire [7:0] led;
    sram dut(wr,rd,address,data_in,cs_n,oe_n,we_n,ram_address,bus,led);
    sram_model memory(cs_n,oe_n,we_n,ram_address,bus);
    reg [3:0] values[0:3];
    integer i;
    initial begin
        values[0]=4'h9; values[1]=4'h6; values[2]=4'hA; values[3]=4'h3;
        #20;
        for(i=0;i<4;i=i+1) begin
            address=i; data_in=values[i]; #10;
            wr=1; #20;
            wr=0; #10;
        end
        data_in=0; #20;
        for(i=0;i<4;i=i+1) begin
            address=i; rd=1; #20;
            if(led !== {4'b0,values[i]}) $fatal(1,"read address=%0d led=%h",i,led);
            rd=0; #10;
        end
        wr=1; rd=1; #20;
        if(bus !== 16'bz || {cs_n,oe_n,we_n} !== 3'b111) $fatal(1,"conflict");
        wr=0; rd=0; #20;
        $display("PASS SRAM view: 4 writes, 4 reads (9 6 a 3), conflict ignored");
        $finish;
    end
endmodule
