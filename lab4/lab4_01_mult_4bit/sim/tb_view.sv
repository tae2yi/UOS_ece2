`timescale 1ns/1ps
// 파형 확인용 TB: 경계값 위주의 입력 12쌍을 10 ns씩 유지합니다.
// 전수 검사는 tb.sv가 맡고, 이 TB는 값을 읽을 수 있는 파형을 만듭니다.
module tb_view;
    reg [3:0] a, b;
    wire [7:0] m;
    mult_4bit dut(a, b, m);
    integer i, checks = 0;
    reg [7:0] vec [0:11];
    initial begin
        vec[0]={4'd0,4'd0};   vec[1]={4'd0,4'd15};  vec[2]={4'd1,4'd9};
        vec[3]={4'd2,4'd8};   vec[4]={4'd3,4'd5};   vec[5]={4'd5,4'd3};
        vec[6]={4'd7,4'd7};   vec[7]={4'd8,4'd8};   vec[8]={4'd9,4'd9};
        vec[9]={4'd12,4'd10}; vec[10]={4'd15,4'd1}; vec[11]={4'd15,4'd15};
        for (i=0; i<12; i=i+1) begin
            {a,b}=vec[i]; #10;
            if (m !== a*b) $fatal(1, "view a=%0d b=%0d m=%0d", a,b,m);
            checks=checks+1;
        end
        $display("PASS multiplier view: %0d directed pairs", checks); $finish;
    end
endmodule
