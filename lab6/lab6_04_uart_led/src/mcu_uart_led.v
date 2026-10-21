`timescale 1ns/1ps
// STM32_2 과제6·7의 FPGA 쪽. LAB3-07 UART 에코를 바탕으로 수신 핀과 동작을 바꿨습니다.
// - mcu_rxd: MCU PC10(UART3 TX)에서 점퍼선으로 받는 입력. XDC에서 확장 GPIO 핀에 연결합니다.
// - uart_txd: 받은 바이트를 그대로 보드 USB-UART(F6)로 PC에 보냅니다(과제6 확인용).
// - led_cmd: 받은 문자가 '0'이면 끄고 '1'이면 켜고 '2'이면 반전, 그 밖의 문자는 유지(과제7).
// - led_byte: 마지막으로 받은 바이트(LAB3 에코와 같은 표시). 과제6에서 PC 출력과 함께 대조합니다.
module mcu_uart_led #(
    parameter integer CLK_HZ = 50_000_000,
    parameter integer BAUD = 9_600
) (
    input  wire clk_50mhz,
    input  wire rst_p,
    input  wire mcu_rxd,
    output wire uart_txd,
    output reg  led_cmd,
    output reg  [6:0] led_byte
);
    localparam integer DIV = (CLK_HZ + BAUD/2) / BAUD;
    wire [7:0] rx_data;
    wire rx_valid;
    wire rx_framing_error;
    wire tx_ready;
    reg tx_valid;
    reg [7:0] tx_data;

    uart_rx #(.DIV(DIV)) u_rx(
        .clk(clk_50mhz), .rst_p(rst_p), .rx(mcu_rxd), .data(rx_data),
        .valid(rx_valid), .framing_error(rx_framing_error));
    uart_tx #(.DIV(DIV)) u_tx(
        .clk(clk_50mhz), .rst_p(rst_p), .valid(tx_valid), .data(tx_data),
        .ready(tx_ready), .tx(uart_txd));

    always @(posedge clk_50mhz) begin
        if (rst_p) begin
            tx_valid <= 0; tx_data <= 0; led_cmd <= 0; led_byte <= 0;
        end else begin
            tx_valid <= 0;
            if (rx_valid) begin
                led_byte <= rx_data[6:0];
                if (tx_ready) begin
                    tx_data <= rx_data;
                    tx_valid <= 1;
                end
                case (rx_data)
                    8'h30: led_cmd <= 1'b0;      // '0'
                    8'h31: led_cmd <= 1'b1;      // '1'
                    8'h32: led_cmd <= ~led_cmd;  // '2'
                    default: led_cmd <= led_cmd;
                endcase
            end
        end
    end
endmodule
