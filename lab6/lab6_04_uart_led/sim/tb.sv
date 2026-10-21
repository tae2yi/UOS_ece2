`timescale 1ns/1ps
// 과제6·7 TB. MCU 호스트 시뮬레이션(stm32_2_hostsim)이 UART3로 보낸 바이트 파일을 읽어
// 그 순서대로 mcu_rxd에 직렬 신호를 넣습니다. 보드용 9600 bps 대신 CLK_HZ=800, BAUD=100
// (한 비트 = 8클록)으로 줄였습니다.
// 검사: 1) FPGA가 PC로 내보낸 바이트가 받은 바이트와 같다(과제6)
//       2) '0'·'1'·'2'·그 밖의 문자에 따른 led_cmd(과제7)  3) led_byte 표시
//       4) 정지 비트가 0인 프레임은 버리고 LED·출력이 그대로다  5) 리셋
module tb;
    localparam integer DIV=8;
    reg clk=0, rst=1, rxd=1;
    always #10 clk=~clk;
    wire txd, led_cmd;
    wire [6:0] led_byte;
    mcu_uart_led #(.CLK_HZ(800), .BAUD(100)) dut(clk,rst,rxd,txd,led_cmd,led_byte);

    reg [7:0] task6[0:15], task7[0:15];
    reg [7:0] observed;
    reg expect_led=0;
    integer i, n, n6, n7, fd, echoes=0;
    reg [7:0] byte_in;


    task send_byte(input [7:0] value, input stop);
        begin
            rxd=0; repeat(DIV) @(posedge clk);
            for(i=0;i<8;i=i+1) begin rxd=value[i]; repeat(DIV) @(posedge clk); end
            rxd=stop; repeat(DIV) @(posedge clk);
            rxd=1; repeat(DIV) @(posedge clk);
        end
    endtask
    task receive_byte(input [7:0] expected);
        integer k;
        begin
            @(negedge txd); repeat(DIV+DIV/2) @(posedge clk);
            for(k=0;k<8;k=k+1) begin observed[k]=txd; repeat(DIV) @(posedge clk); end
            if(observed!==expected) $fatal(1,"PC output %h expected %h",observed,expected);
            echoes=echoes+1;
        end
    endtask
    task command(input [7:0] value);
        begin
            fork send_byte(value,1'b1); receive_byte(value); join
            case(value)
                8'h30: expect_led=0;
                8'h31: expect_led=1;
                8'h32: expect_led=!expect_led;
                default: ;
            endcase
            if(led_cmd!==expect_led) $fatal(1,"after %h led_cmd=%b expected %b",value,led_cmd,expect_led);
            if(led_byte!==value[6:0]) $fatal(1,"led_byte=%h expected %h",led_byte,value[6:0]);
            $display("  %s 0x%h -> PC 0x%h, led_cmd=%b", (value>=8'h20 && value<8'h7f) ? value : "?",
                     value, observed, led_cmd);
        end
    endtask
    initial begin
        // 한 줄에 16진수 한 바이트. $fscanf는 파일 끝에서 -1을 돌려준다.
        fd=$fopen("sim/mcu_task6.hex","r"); n6=0;
        if(fd==0) $fatal(1,"sim/mcu_task6.hex");
        while(n6<16 && $fscanf(fd,"%h",byte_in)==1) begin task6[n6]=byte_in; n6=n6+1; end
        $fclose(fd);
        fd=$fopen("sim/mcu_task7.hex","r"); n7=0;
        if(fd==0) $fatal(1,"sim/mcu_task7.hex");
        while(n7<16 && $fscanf(fd,"%h",byte_in)==1) begin task7[n7]=byte_in; n7=n7+1; end
        $fclose(fd);
        repeat(4) @(posedge clk); rst=0;
        $display("task6 bytes from MCU host simulation:");
        if(n6!==3) $fatal(1,"task6 hex has %0d bytes",n6);
        for(n=0; n<n6; n=n+1) command(task6[n]);
        $display("task7 commands from MCU host simulation:");
        if(n7!==9) $fatal(1,"task7 hex has %0d bytes",n7);
        for(n=0; n<n7; n=n+1) command(task7[n]);
        // 정지 비트 오류: '0'을 보내지만 정지 비트가 0이면 버린다(LED 1 유지, PC 출력 없음).
        send_byte(8'h30,1'b0);
        repeat(4*DIV) @(posedge clk);
        if(led_cmd!==1 || txd!==1) $fatal(1,"framing error frame was accepted");
        rst=1; @(posedge clk); #1;
        if(led_cmd!==0 || led_byte!==0 || txd!==1) $fatal(1,"reset");
        $display("PASS uart_led: %0d bytes echoed, LED commands 0/1/2/other, framing error, reset", echoes);
        $finish;
    end
    initial begin #200000; $fatal(1,"timeout"); end
endmodule
