`timescale 1ns/1ps
// 파형 확인용 TB: 송신 간격 40 us, SCK 500 kHz로 0x55, 0xA5 두 바이트를 본다.
// CS_n LOW와 동시에 MOSI에 bit7이 준비되고, 1 us 뒤 첫 상승 에지, 하강 에지마다 MOSI가 다음 비트로 바뀌는지,
// state(1 LEAD, 2 HIGH, 3 LOW, 4 TRAIL, 5 GAP)와 bit_index가 어떻게 움직이는지 확인한다.
module tb_view;
    reg clk = 0, rst = 1;
    always #10 clk = ~clk;
    wire sck, mosi, cs_n, txd;
    wire [7:0] led;
    spi_tx_uart #(.BAUD(1_000_000), .PERIOD_CLKS(2_000)) dut(
        .clk_50mhz(clk), .rst_p(rst), .spi_sck(sck), .spi_mosi(mosi), .spi_cs_n(cs_n),
        .uart_txd(txd), .led(led));
    reg [7:0] got;
    integer n = 0;
    always @(negedge cs_n) got = 0;
    always @(posedge sck) got = {got[6:0], mosi};
    always @(posedge cs_n) if (!rst) begin
        if (got !== (n == 0 ? 8'h55 : 8'hA5)) $fatal(1, "byte %0d = %02X", n, got);
        n = n + 1;
    end
    initial begin
        repeat (5) @(posedge clk); rst = 0;
        wait (n == 2);
        #20000;   // (세 번째 바이트 120 us 전에 끝) 두 바이트가 파형 위·아래 절반에 하나씩 오도록 끝을 늘림
        $display("PASS spi_tx view: 0x55, 0xA5 sent MSB first, SCK 500 kHz");
        $finish;
    end
endmodule
