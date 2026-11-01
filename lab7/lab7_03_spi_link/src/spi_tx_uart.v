`timescale 1ns/1ps
// STM32_3 과제11 · 과제12 송신 측 최상위: 1초마다 한 바이트를 SPI 마스터로 보냅니다.
// - 보내는 값: 매뉴얼의 비교값 0x55 -> 0xA5 -> 0x00 -> 0xFF를 차례로 반복(MCU 송신 예제와 같은 순서).
// - spi_sck, spi_mosi, spi_cs_n: BDIO_0~2로 내보내 MCU(PB3, PA7, PA4) 또는 상대 FPGA에 연결.
// - uart_txd: 보낸 값을 "TX=55\r\n"으로 PC에 알립니다(받는 쪽 "RX=55"와 비교용).
// - led: 마지막으로 보낸 바이트. LED1 = bit7.
// PERIOD_CLKS: 송신 간격(기본 50,000,000클록 = 1 s). SCK_HALF: SCK 반주기 클록 수(기본 50 = 500 kHz).
module spi_tx_uart #(
    parameter integer CLK_HZ = 50_000_000,
    parameter integer BAUD = 9_600,
    parameter integer PERIOD_CLKS = 50_000_000,
    parameter integer SCK_HALF = 50
) (
    input  wire clk_50mhz,
    input  wire rst_p,
    output wire spi_sck,
    output wire spi_mosi,
    output wire spi_cs_n,
    output wire uart_txd,
    output reg  [7:0] led
);
    localparam integer DIV = (CLK_HZ + BAUD/2) / BAUD;
    reg [$clog2(PERIOD_CLKS)-1:0] timer;
    reg [1:0] index;
    reg start;
    reg [7:0] value;
    wire busy, done;
    wire line_busy, line_dropped;

    function [7:0] pattern(input [1:0] i);
        case (i)
            2'd0: pattern = 8'h55;
            2'd1: pattern = 8'hA5;
            2'd2: pattern = 8'h00;
            default: pattern = 8'hFF;
        endcase
    endfunction

    // 1초 타이머: 리셋 후 1초가 지나면 첫 바이트, 이후 1초마다
    always @(posedge clk_50mhz) begin
        if (rst_p) begin
            timer <= 0; index <= 0; start <= 0; value <= 0; led <= 0;
        end else begin
            start <= 0;
            if (timer == PERIOD_CLKS - 1) begin
                timer <= 0;
                if (!busy) begin
                    value <= pattern(index);
                    start <= 1;
                    index <= index + 1'b1;
                end
            end else
                timer <= timer + 1'b1;
            if (done) led <= value;
        end
    end

    spi_master_tx #(.HALF(SCK_HALF)) u_spi(
        .clk(clk_50mhz), .rst_p(rst_p), .start(start), .data(value),
        .sck(spi_sck), .mosi(spi_mosi), .cs_n(spi_cs_n), .busy(busy), .done(done));

    hex_line_tx #(.DIV(DIV), .PREFIX("TX=")) u_line(
        .clk(clk_50mhz), .rst_p(rst_p), .start(done), .value(value),
        .busy(line_busy), .dropped(line_dropped), .txd(uart_txd));
endmodule
