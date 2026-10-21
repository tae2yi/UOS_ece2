`timescale 1ns/1ps
module servo_ctrl #(parameter CLK_HZ=50_000_000)(
    input wire clk_50mhz,rst_p,left_pulse,right_pulse,
    output wire servo
);
    wire [31:0] pulse_us;
    servo_position u_position(clk_50mhz,rst_p,left_pulse,right_pulse,pulse_us);
    servo_pwm #(.CLK_HZ(CLK_HZ)) u_pwm(clk_50mhz,rst_p,pulse_us,servo);
endmodule
