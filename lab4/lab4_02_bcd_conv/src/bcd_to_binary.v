`timescale 1ns/1ps
// 십의 자리와 일의 자리를 각각 0~9로 입력합니다.
module bcd_to_binary(
    input wire [3:0] ten, one,
    output wire [6:0] binary,
    output wire valid
);
    assign binary = ten * 7'd10 + one;
    assign valid = (ten <= 9) && (one <= 9);
endmodule
