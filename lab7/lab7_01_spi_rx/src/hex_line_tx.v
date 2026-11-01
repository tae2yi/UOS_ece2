`timescale 1ns/1ps
// 한 바이트를 MCU 출력과 같은 모양의 글 한 줄로 UART에 보냅니다.
// 예: PREFIX="RX=", value=8'hA5 -> "RX=A5\r\n" (7글자, 9600 bps에서 약 7.3 ms)
// start는 busy=0일 때만 받습니다. busy 중에 들어온 start는 버리고 dropped를 한 클록 1로 만듭니다.
module hex_line_tx #(
    parameter integer DIV = 5208,
    parameter [23:0] PREFIX = "RX="
) (
    input  wire clk,
    input  wire rst_p,
    input  wire start,
    input  wire [7:0] value,
    output wire busy,
    output reg  dropped,
    output wire txd
);
    reg [7:0] latched;
    reg [2:0] index;      // 지금 보낼 글자 번호 0~6
    reg active;
    reg tx_valid;
    reg [7:0] tx_data;
    wire tx_ready;

    uart_tx #(.DIV(DIV)) u_tx(
        .clk(clk), .rst_p(rst_p), .valid(tx_valid), .data(tx_data),
        .ready(tx_ready), .tx(txd));

    function [7:0] hex_char(input [3:0] nibble);
        hex_char = nibble < 4'd10 ? 8'h30 + nibble : 8'h37 + nibble; // '0'~'9', 'A'~'F'
    endfunction

    function [7:0] char_at(input [2:0] i, input [7:0] v);
        case (i)
            3'd0: char_at = PREFIX[23:16];
            3'd1: char_at = PREFIX[15:8];
            3'd2: char_at = PREFIX[7:0];
            3'd3: char_at = hex_char(v[7:4]);
            3'd4: char_at = hex_char(v[3:0]);
            3'd5: char_at = 8'h0D;   // \r
            default: char_at = 8'h0A; // \n
        endcase
    endfunction

    assign busy = active;

    always @(posedge clk) begin
        if (rst_p) begin
            latched <= 0; index <= 0; active <= 0;
            tx_valid <= 0; tx_data <= 0; dropped <= 0;
        end else begin
            tx_valid <= 0;
            dropped <= 0;
            if (!active) begin
                if (start) begin
                    latched <= value; index <= 0; active <= 1;
                end
            end else begin
                if (start) dropped <= 1;
                // uart_tx가 비어 있고 직전 클록에 글자를 넘기지 않았을 때 다음 글자를 넘긴다
                if (tx_ready && !tx_valid) begin
                    tx_data <= char_at(index, latched);
                    tx_valid <= 1;
                    if (index == 3'd6) active <= 0;
                    else index <= index + 1'b1;
                end
            end
        end
    end
endmodule
