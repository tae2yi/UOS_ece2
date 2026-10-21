`timescale 1ns/1ps
// 파형 확인용 TB: 한 비트 = 8클록(160 ns)으로 줄여 '1', '2', '2', '0'을 차례로 보냅니다.
// 바이트마다 rx_valid 다음 클록에 led_cmd가 1 -> 0 -> 1 -> 0으로 바뀌고,
// 같은 바이트가 uart_txd로 PC에 나가는지 봅니다.
module tb_view;
    localparam integer DIV=8;
    reg clk=0, rst=1, rxd=1;
    always #10 clk=~clk;
    wire txd, led_cmd;
    wire [6:0] led_byte;
    mcu_uart_led #(.CLK_HZ(800), .BAUD(100)) dut(clk,rst,rxd,txd,led_cmd,led_byte);
    reg [7:0] seq[0:3];
    reg want[0:3];
    integer i, b;
    task send_byte(input [7:0] value);
        begin
            rxd=0; repeat(DIV) @(posedge clk);
            for(i=0;i<8;i=i+1) begin rxd=value[i]; repeat(DIV) @(posedge clk); end
            rxd=1; repeat(DIV) @(posedge clk);
        end
    endtask
    initial begin
        seq[0]="1"; seq[1]="2"; seq[2]="2"; seq[3]="0";
        want[0]=1; want[1]=0; want[2]=1; want[3]=0;
        repeat(4) @(posedge clk); rst=0;
        repeat(8) @(posedge clk);
        for(b=0;b<4;b=b+1) begin
            send_byte(seq[b]);
            repeat(6*DIV) @(posedge clk);   // PC로 나가는 에코가 끝날 때까지 쉼
            if(led_cmd!==want[b]) $fatal(1,"byte %0d led_cmd=%b",b,led_cmd);
        end
        repeat(8) @(posedge clk);
        $display("PASS uart_led view: 1 2 2 0 -> led_cmd 1 0 1 0");
        $finish;
    end
endmodule
