`timescale 1ns/1ps
// 파형 확인용 TB: 유효 입력 8개와 범위를 벗어난 입력 4개를 10 ns씩 유지합니다.
// 전수 검사는 tb.sv가 맡고, 이 TB는 값을 읽을 수 있는 파형을 만듭니다.
module tb_view;
    reg [3:0] ten, one;
    wire [6:0] bin;
    wire valid;
    bcd_conv dut(one, ten, bin, valid);
    integer i, checks = 0;
    reg [7:0] vec [0:11];
    initial begin
        vec[0]={4'd0,4'd0};   vec[1]={4'd0,4'd9};   vec[2]={4'd1,4'd0};
        vec[3]={4'd2,4'd5};   vec[4]={4'd4,4'd2};   vec[5]={4'd6,4'd4};
        vec[6]={4'd9,4'd0};   vec[7]={4'd9,4'd9};   vec[8]={4'd10,4'd0};
        vec[9]={4'd0,4'd10};  vec[10]={4'd12,4'd7}; vec[11]={4'd15,4'd15};
        for (i=0; i<12; i=i+1) begin
            {ten,one}=vec[i]; #10;
            if (valid !== ((ten<10)&&(one<10))) $fatal(1, "view valid");
            if (bin !== ((ten*10+one) & 7'h7f)) $fatal(1, "view bin");
            checks=checks+1;
        end
        $display("PASS BCD view: %0d directed inputs", checks); $finish;
    end
endmodule
