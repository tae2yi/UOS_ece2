`timescale 1ns/1ps
module servo_pwm #(parameter CLK_HZ=50_000_000)(
    input wire clk_50mhz,rst_p,
    input wire [31:0] pulse_us,
    output wire servo
);
    localparam FRAME_CYCLES=CLK_HZ/50; // 20 ms
    reg [31:0] count;
    reg [31:0] width_cycles;
    always @(posedge clk_50mhz) begin
        if(rst_p) begin
            count<=0; width_cycles<=(CLK_HZ/1000)*3/2;
        end
        else if(count==FRAME_CYCLES-1) begin
            count<=0;
            // 프레임 경계에서만 폭을 바꿔 중간 펄스가 잘리지 않게 합니다.
            width_cycles<=pulse_us*(CLK_HZ/1000)/1000;
        end
        else count<=count+1;
    end
    assign servo=!rst_p && (count<width_cycles);
endmodule
