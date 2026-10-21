`timescale 1ns/1ps
// 파형 확인용 TB: 보드용 top servo_board를 CLK_HZ=10000으로 검사합니다.
// 한 프레임(20 ms)이 200클록(2 us), 1 ms가 10클록이므로 펄스 폭 1.5 ms = 15클록입니다.
// 버튼은 누를 때 떨림 3번을 넣고, button_pulse(STABLE_CYCLES=4)가 한 펄스로 만드는지 봅니다.
// 1프레임 1500 us -> 왼쪽 1번 -> 1400 us -> 오른쪽 3번 -> 1700 us.
module tb_view;
    reg clk=0, rst=1, left=0, right=0;
    always #5 clk=~clk;
    wire servo;
    servo_board #(.CLK_HZ(10000), .STABLE_CYCLES(4)) dut(clk,rst,left,right,servo);
    integer i, high, frames=0;
    integer widths[0:3];
    // 버튼 누름: 1클록 간격으로 3번 떨린 뒤 hold클록 동안 누르고 뗍니다.
    task press(input bit is_left, input integer hold);
        begin
            for(i=0;i<3;i=i+1) begin
                @(negedge clk); if(is_left) left=1; else right=1;
                @(negedge clk); left=0; right=0;
            end
            @(negedge clk); if(is_left) left=1; else right=1;
            repeat(hold) @(negedge clk);
            left=0; right=0;
            repeat(10) @(negedge clk);
        end
    endtask
    // 프레임마다 HIGH 클록 수를 셉니다.
    always @(posedge clk) if(!rst) begin
        if(dut.u_servo.u_pwm.count==0) begin
            if(frames>0 && frames<=4) widths[frames-1]=high;
            high=0; frames=frames+1;
        end
        if(servo) high=high+1;
    end
    initial begin
        high=0;
        repeat(3) @(negedge clk); rst=0;
        repeat(40) @(negedge clk);
        press(1, 12);                 // 1프레임 중: 왼쪽 -> 1400
        wait(frames==2); repeat(30) @(negedge clk);
        repeat(3) press(0, 8);        // 2프레임 중: 오른쪽 3번 -> 1700
        wait(frames==5);
        if(widths[0]!==15 || widths[1]!==14 || widths[2]!==17 || widths[3]!==17)
            $fatal(1,"widths %0d %0d %0d %0d",widths[0],widths[1],widths[2],widths[3]);
        if(dut.u_servo.pulse_us!==1700) $fatal(1,"pulse_us %0d",dut.u_servo.pulse_us);
        $display("PASS servo view: bounce -> one step, widths 15/14/17/17 clocks");
        $finish;
    end
    initial begin #20000; $fatal(1,"timeout"); end
endmodule
