`timescale 1ns/1ps
// 파형 확인용 TB: 보드 A(마스터)가 0x55, 0xA5를 보내고 보드 B(수신)가 받는 과정을 한 화면에 놓는다.
// A의 sck·mosi·cs_n과 B 안의 동기화된 상승 에지(sck_rise)·bit_count·rx_valid·rx_data를 함께 본다.
// 두 보드 클록은 따로(A 20 ns, B 20.05 ns), UART는 1 Mbps로 줄였다.
module tb_view;
    reg clk_a = 0, clk_b = 0, rst = 1;
    always #10 clk_a = ~clk_a;
    initial begin #7; forever #10.025 clk_b = ~clk_b; end
    wire sck_a, mosi_a, cs_n_a, txd_a, txd_b;
    wire [7:0] led_a, led_b;
    wire #3 sck_b = sck_a;
    wire #5 mosi_b = mosi_a;
    wire #4 cs_n_b = cs_n_a;
    spi_tx_uart #(.BAUD(1_000_000), .PERIOD_CLKS(2_000)) board_a(
        .clk_50mhz(clk_a), .rst_p(rst), .spi_sck(sck_a), .spi_mosi(mosi_a), .spi_cs_n(cs_n_a),
        .uart_txd(txd_a), .led(led_a));
    spi_rx_uart #(.BAUD(1_000_000)) board_b(
        .clk_50mhz(clk_b), .rst_p(rst), .spi_sck(sck_b), .spi_mosi(mosi_b), .spi_cs_n(cs_n_b),
        .uart_txd(txd_b), .led(led_b));
    integer n = 0;
    always @(posedge clk_b) if (board_b.rx_valid) begin
        if (board_b.rx_data !== (n == 0 ? 8'h55 : 8'hA5)) $fatal(1, "B got %02X", board_b.rx_data);
        n = n + 1;
    end
    initial begin
        repeat (5) @(posedge clk_a); rst = 0;
        wait (n == 2);
        #20000;   // (세 번째 바이트 120 us 전에 끝) 두 바이트가 파형 위·아래 절반에 하나씩 오도록 끝을 늘림
        $display("PASS spi_link view: B received 0x55, 0xA5 from A");
        $finish;
    end
endmodule
