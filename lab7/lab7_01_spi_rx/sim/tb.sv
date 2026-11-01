`timescale 1ns/1ps
// STM32_3 과제10 TB: MCU 마스터 → FPGA 수신 → FPGA UART(9600) → PC
// - 보낼 바이트는 MCU 호스트 시뮬레이션이 HAL_SPI_Transmit으로 보낸 값(sim/mcu_spi.hex, 0x55 0xA5 0x00 0xFF 반복)이다.
// - SPI 타이밍은 MCU 기본 설정과 같게: SCK 781.25 kHz(반주기 640 ns), Mode 0, MSB 먼저.
//   CS LOW 뒤 첫 상승 에지까지 3 us, 마지막 하강 에지 뒤 CS HIGH까지 2 us(HAL 함수 호출 시간 정도).
//   바이트 사이 간격은 1 s 대신 10 ms로 줄였다(UART 한 줄 7.3 ms보다 길면 동작은 같다).
// - 확인: (1) UART로 나온 글이 "RX=<보낸 값>\r\n"인지, (2) LED가 보낸 값인지,
//         (3) 4비트만 보내고 CS를 올린 뒤(끊긴 바이트) 보낸 0x3C를 0x3C로 받는지.
module tb;
    localparam integer HALF_NS = 640;
    localparam integer BIT_NS = 5208 * 20;   // uart DIV(5208) x 20 ns
    reg clk = 0, rst = 1;
    reg sck = 0, mosi = 0, cs_n = 1;
    always #10 clk = ~clk;
    wire txd;
    wire [7:0] led;
    spi_rx_uart dut(.clk_50mhz(clk), .rst_p(rst), .spi_sck(sck), .spi_mosi(mosi),
                    .spi_cs_n(cs_n), .uart_txd(txd), .led(led));

    reg [7:0] mcu_bytes [0:7];
    reg [7:0] expect_q [0:15];
    integer n_expect = 0, n_lines = 0, errors = 0;

    // Mode 0 송신: 첫 비트를 CS LOW와 함께 준비, 상승 에지 전 반주기, 하강 에지에서 다음 비트
    task spi_send(input [7:0] value, input integer nbits);
        integer i;
        begin
            cs_n = 0; mosi = value[7];
            #(3000 - HALF_NS);
            for (i = 7; i > 7 - nbits; i = i - 1) begin
                mosi = value[i];
                #HALF_NS sck = 1;
                #HALF_NS sck = 0;
            end
            #2000 cs_n = 1;
        end
    endtask

    // PC 쪽 UART 수신: 글자를 모아 \n이 오면 한 줄을 기대값과 비교
    reg [7:0] line [0:15];
    integer len = 0;
    task check_line;
        reg [7:0] want;
        reg [8*8-1:0] got;
        integer k;
        begin
            want = expect_q[n_lines];
            got = 0;
            for (k = 0; k < len; k = k + 1) got = {got[8*7-1:0], line[k]};
            if (len != 7 || line[0] != "R" || line[1] != "X" || line[2] != "=" ||
                line[3] != hex(want[7:4]) || line[4] != hex(want[3:0]) ||
                line[5] != 8'h0D || line[6] != 8'h0A) begin
                $display("FAIL line %0d: want RX=%02X, got %0d chars", n_lines, want, len);
                errors = errors + 1;
            end else
                $display("t=%7.3f ms  UART line %0d: \"RX=%c%c\\r\\n\"  LED=%c%c", $realtime/1e6, n_lines, line[3], line[4], hex(led[7:4]), hex(led[3:0]));
            if (led !== want) begin
                $display("FAIL led=%02X want %02X", led, want);
                errors = errors + 1;
            end
            n_lines = n_lines + 1;
            len = 0;
        end
    endtask
    function [7:0] hex(input [3:0] v);
        hex = v < 10 ? 8'h30 + v : 8'h37 + v;
    endfunction

    initial begin : uart_monitor
        reg [7:0] ch;
        integer b;
        forever begin
            @(negedge txd);
            #(BIT_NS + BIT_NS/2);
            for (b = 0; b < 8; b = b + 1) begin ch[b] = txd; #(BIT_NS); end
            if (txd !== 1'b1) begin $display("FAIL framing"); errors = errors + 1; end
            line[len] = ch; len = len + 1;
            if (ch == 8'h0A) check_line;
        end
    end

    integer j;
    initial begin
        $readmemh("sim/mcu_spi.hex", mcu_bytes);
        repeat (5) @(posedge clk); rst = 0;
        #20000;
        for (j = 0; j < 8; j = j + 1) begin
            expect_q[n_expect] = mcu_bytes[j]; n_expect = n_expect + 1;
            spi_send(mcu_bytes[j], 8);
            #10_000_000;
        end
        // 끊긴 바이트: 4비트(1111)만 보내고 CS HIGH → 카운터가 0으로 돌아가야 한다
        spi_send(8'hF0, 4);
        #50_000;
        expect_q[n_expect] = 8'h3C; n_expect = n_expect + 1;
        spi_send(8'h3C, 8);
        #10_000_000;
        if (n_lines != n_expect) begin
            $display("FAIL: %0d lines, want %0d", n_lines, n_expect); errors = errors + 1;
        end
        if (errors == 0)
            $display("PASS spi_rx tb: %0d bytes from MCU hostsim + partial-byte recovery 0x3C, UART lines and LED match", n_expect);
        else
            $fatal(1, "spi_rx tb: %0d errors", errors);
        $finish;
    end
endmodule
