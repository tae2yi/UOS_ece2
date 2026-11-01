`timescale 1ns/1ps
// STM32_3 과제12 TB: FPGA 보드 A(lab7_02 마스터 송신) → FPGA 보드 B(lab7_01 슬레이브 수신)
// 실제처럼 두 보드의 클록을 따로 둔다: A = 20.000 ns, B = 20.050 ns(0.25% 느림, 위상도 7 ns 어긋남).
// 점퍼선·버스 스위치 지연으로 SCK·MOSI·CS_n에 각각 3·5·4 ns를 더한다.
// 송신 간격만 10 ms로 줄였다. 확인: B의 UART가 "RX=<A가 보낸 값>"을 같은 순서로 내는지, A의 UART "TX=" 줄과 일치하는지.
// 역할 교대는 두 보드의 bitstream을 바꿔 올리는 것이므로 같은 회로·같은 결과다.
module tb;
    localparam integer NBYTES = 8;
    localparam integer BIT_NS = 5208 * 20;
    reg clk_a = 0, clk_b = 0, rst = 1;
    always #10 clk_a = ~clk_a;
    initial begin #7; forever #10.025 clk_b = ~clk_b; end

    wire sck_a, mosi_a, cs_n_a, txd_a, txd_b;
    wire [7:0] led_a, led_b;
    wire #3 sck_b = sck_a;
    wire #5 mosi_b = mosi_a;
    wire #4 cs_n_b = cs_n_a;

    spi_tx_uart #(.PERIOD_CLKS(500_000)) board_a(
        .clk_50mhz(clk_a), .rst_p(rst), .spi_sck(sck_a), .spi_mosi(mosi_a), .spi_cs_n(cs_n_a),
        .uart_txd(txd_a), .led(led_a));
    spi_rx_uart board_b(
        .clk_50mhz(clk_b), .rst_p(rst), .spi_sck(sck_b), .spi_mosi(mosi_b), .spi_cs_n(cs_n_b),
        .uart_txd(txd_b), .led(led_b));

    function [7:0] hex(input [3:0] v);
        hex = v < 10 ? 8'h30 + v : 8'h37 + v;
    endfunction
    function [3:0] unhex(input [7:0] c);
        unhex = c <= "9" ? c - "0" : c - "A" + 10;
    endfunction

    // PC 두 대(각 보드의 USB-UART)에 나온 줄을 모은다
    reg [7:0] tx_vals [0:15];
    reg [7:0] rx_vals [0:15];
    integer n_tx = 0, n_rx = 0, errors = 0;
    task automatic uart_pc(input integer which);
        reg [7:0] ch;
        reg [7:0] line [0:7];
        integer b, len;
        begin
            len = 0;
            forever begin
                if (which == 0) @(negedge txd_a); else @(negedge txd_b);
                #(BIT_NS + BIT_NS/2);
                for (b = 0; b < 8; b = b + 1) begin
                    ch[b] = (which == 0) ? txd_a : txd_b; #(BIT_NS);
                end
                if (len < 8) line[len] = ch;
                len = len + 1;
                if (ch == 8'h0A) begin
                    if (len != 7 || line[1] != "X" || line[2] != "=") begin
                        $display("FAIL board %s line format", which == 0 ? "A" : "B"); errors = errors + 1;
                    end
                    if (which == 0) begin
                        tx_vals[n_tx] = {unhex(line[3]), unhex(line[4])}; n_tx = n_tx + 1;
                    end else begin
                        rx_vals[n_rx] = {unhex(line[3]), unhex(line[4])};
                        $display("t=%7.3f ms  A: \"TX=%c%c\"  B: \"RX=%c%c\"  B LED=%c%c",
                                 $realtime/1e6, hex(tx_vals[n_rx][7:4]), hex(tx_vals[n_rx][3:0]),
                                 line[3], line[4], hex(led_b[7:4]), hex(led_b[3:0]));
                        n_rx = n_rx + 1;
                    end
                    len = 0;
                end
            end
        end
    endtask
    initial uart_pc(0);
    initial uart_pc(1);

    integer k;
    initial begin
        repeat (5) @(posedge clk_a); rst = 0;
        wait (n_rx == NBYTES);
        #1000;
        for (k = 0; k < NBYTES; k = k + 1)
            if (rx_vals[k] !== tx_vals[k]) begin
                $display("FAIL byte %0d: A sent %02X, B got %02X", k, tx_vals[k], rx_vals[k]); errors = errors + 1;
            end
        if (errors == 0)
            $display("PASS spi_link tb: board A TX = board B RX for %0d bytes (separate clocks, wire delay)", NBYTES);
        else
            $fatal(1, "spi_link tb: %0d errors", errors);
        $finish;
    end
endmodule
