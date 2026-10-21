`timescale 1ns/1ps
// 보드용 top. 매뉴얼의 servo_ctrl은 한 클록 펄스를 입력으로 받으므로
// 버튼 두 개를 button_pulse로 거쳐 연결합니다. 시뮬레이션은 servo_ctrl도 직접 검사합니다.
module servo_board #(parameter CLK_HZ=50_000_000, STABLE_CYCLES=CLK_HZ/50)(
    input wire clk_50mhz,rst_p,button_left,button_right,
    output wire servo
);
    wire left_pulse,right_pulse;
    button_pulse #(.STABLE_CYCLES(STABLE_CYCLES)) u_left(clk_50mhz,rst_p,button_left,left_pulse);
    button_pulse #(.STABLE_CYCLES(STABLE_CYCLES)) u_right(clk_50mhz,rst_p,button_right,right_pulse);
    servo_ctrl #(.CLK_HZ(CLK_HZ)) u_servo(clk_50mhz,rst_p,left_pulse,right_pulse,servo);
endmodule
