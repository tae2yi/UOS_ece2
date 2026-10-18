`timescale 1ns/1ps
// 파형 확인용 TB: HALF_CYCLES=2라서 직렬 클록 한 주기가 4클록(40 ns)입니다.
// 채널 2 명령 한 프레임(16비트)을 보내고 ADC 모델이 16'hA5C3으로 응답합니다.
// sample은 하위 12비트 12'h5C3, led_out은 sample[11:4]=8'h5C가 되어야 합니다.
module tb_view;
    reg clk=0, rst=1;
    always #5 clk=~clk;
    reg [2:0] channel=2;
    reg miso=0;
    wire sclk,cs_n,mosi,valid;
    wire [11:0] sample;
    wire [7:0] led;
    adc #(.HALF_CYCLES(2)) dut(clk,rst,channel,sclk,cs_n,mosi,miso,sample,valid,led);
    reg [15:0] reply=16'hA5C3;
    reg [15:0] received_command=0, frame_command;
    integer bit_no=15, bits=0;
    // ADC 모델: 하강 에지에서 응답 비트 준비, 상승 에지에서 명령 수신.
    always @(negedge cs_n) begin bit_no=15; bits=0; received_command=0; end
    always @(negedge sclk) if(!cs_n) miso=reply[bit_no];
    // 마지막 상승 에지와 cs_n 해제가 같은 클록이므로 cs_n 대신 비트 수로 끊습니다.
    always @(posedge sclk) if(!rst && bits<16) begin
        received_command={received_command[14:0],mosi}; bit_no=bit_no-1; bits=bits+1;
    end
    initial begin
        repeat(2) @(negedge clk); rst=0;
        @(posedge valid); #1;
        frame_command=received_command; // 다음 프레임이 곧 시작되므로 값을 보관
        if(frame_command !== 16'hAB70) $fatal(1,"command %h",frame_command);
        if(sample !== 12'h5C3 || led !== 8'h5C) $fatal(1,"sample %h led %h",sample,led);
        repeat(12) @(negedge clk);
        $display("PASS ADC view: command %h, sample %h, led %h", frame_command, sample, led);
        $finish;
    end
endmodule
