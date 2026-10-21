`timescale 1ns/1ps
// 버튼은 동기화·디바운스 후 한 클록 길이의 펄스로 전달합니다.
module servo_position(
    input wire clk_50mhz,rst_p,left_pulse,right_pulse,
    output reg [31:0] pulse_us
);
    always @(posedge clk_50mhz)
        if(rst_p) pulse_us<=1500;
        else if(left_pulse && !right_pulse && pulse_us>1000) pulse_us<=pulse_us-100;
        else if(right_pulse && !left_pulse && pulse_us<2000) pulse_us<=pulse_us+100;
endmodule
