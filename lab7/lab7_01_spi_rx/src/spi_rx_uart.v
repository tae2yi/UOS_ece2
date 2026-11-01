`timescale 1ns/1ps
// STM32_3 과제10 · 과제12 수신 측 최상위: SPI로 받은 바이트를 FPGA UART로 PC에 보냅니다.
// - spi_sck, spi_mosi, spi_cs_n: MCU(PB3, PA7, PB6) 또는 상대 FPGA에서 점퍼선으로 받는 입력(BDIO_0~2).
// - uart_txd: 보드 USB-UART(F6). 받은 값을 MCU 출력과 같은 모양 "RX=55\r\n"으로 보냅니다(9600 8N1).
// - led: 마지막으로 받은 바이트. LED1 = 최상위 비트(bit7), LED8 = bit0.
module spi_rx_uart #(
    parameter integer CLK_HZ = 50_000_000,
    parameter integer BAUD = 9_600
) (
    input  wire clk_50mhz,
    input  wire rst_p,
    input  wire spi_sck,
    input  wire spi_mosi,
    input  wire spi_cs_n,
    output wire uart_txd,
    output reg  [7:0] led
);
    localparam integer DIV = (CLK_HZ + BAUD/2) / BAUD;
    wire [7:0] rx_data;
    wire rx_valid;
    wire [2:0] bit_count;
    wire sck_rise;
    wire line_busy;
    wire line_dropped;

    spi_slave_rx u_spi(
        .clk(clk_50mhz), .rst_p(rst_p), .sck(spi_sck), .mosi(spi_mosi), .cs_n(spi_cs_n),
        .data(rx_data), .valid(rx_valid), .bit_count_o(bit_count), .sck_rise_o(sck_rise));

    hex_line_tx #(.DIV(DIV), .PREFIX("RX=")) u_line(
        .clk(clk_50mhz), .rst_p(rst_p), .start(rx_valid), .value(rx_data),
        .busy(line_busy), .dropped(line_dropped), .txd(uart_txd));

    always @(posedge clk_50mhz) begin
        if (rst_p) led <= 0;
        else if (rx_valid) led <= rx_data;
    end
endmodule
