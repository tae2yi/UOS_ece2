`timescale 1ns/1ps
// UART 송신 8N1. lab6_04_uart_led(LAB3-07 UART 에코 바탕)의 uart_tx와 같은 동작입니다.
// ready=1일 때 valid를 한 클록 주면 data를 시작 비트, 데이터 8비트(LSB 먼저), 정지 비트 순서로 보냅니다.
module uart_tx #(parameter integer DIV = 5208)(
    input wire clk, rst_p, valid,
    input wire [7:0] data,
    output wire ready,
    output wire tx
);
    reg [9:0] shift;
    reg [3:0] remaining;
    integer timer;
    assign ready = (remaining == 0);
    assign tx = ready ? 1'b1 : shift[0];
    always @(posedge clk) begin
        if(rst_p) begin shift<=10'h3ff; remaining<=0; timer<=0; end
        else if(ready) begin
            if(valid) begin shift<={1'b1,data,1'b0}; remaining<=10; timer<=DIV-1; end
        end else if(timer!=0) timer<=timer-1;
        else begin timer<=DIV-1; shift<={1'b1,shift[9:1]}; remaining<=remaining-1'b1; end
    end
endmodule
