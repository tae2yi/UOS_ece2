`timescale 1ns/1ps
// 파형 확인용 TB: MCU 타이밍(SCK 781.25 kHz)으로 0x55, 0xA5 두 바이트를 보낸다.
// 동기화된 SCK의 상승 에지(sck_rise)마다 bit_count가 0 -> 7로 늘고, 8번째 에지에서 valid와 data가 나오는지,
// CS가 HIGH인 사이에 bit_count가 0으로 돌아가는지 본다. UART는 1 Mbps로 줄여 같은 화면에서 "RX=55" 줄을 본다.
module tb_view;
    localparam integer HALF_NS = 640;
    reg clk = 0, rst = 1;
    reg sck = 0, mosi = 0, cs_n = 1;
    always #10 clk = ~clk;
    wire txd;
    wire [7:0] led;
    spi_rx_uart #(.CLK_HZ(50_000_000), .BAUD(1_000_000)) dut(
        .clk_50mhz(clk), .rst_p(rst), .spi_sck(sck), .spi_mosi(mosi),
        .spi_cs_n(cs_n), .uart_txd(txd), .led(led));

    task spi_send(input [7:0] value);
        integer i;
        begin
            cs_n = 0; mosi = value[7];
            #(3000 - HALF_NS);
            for (i = 7; i >= 0; i = i - 1) begin
                mosi = value[i];
                #HALF_NS sck = 1;
                #HALF_NS sck = 0;
            end
            #2000 cs_n = 1;
        end
    endtask

    initial begin
        repeat (5) @(posedge clk); rst = 0;
        #2000;
        spi_send(8'h55);
        if (dut.rx_data !== 8'h55) $fatal(1, "rx_data=%02X", dut.rx_data);
        #6000;
        spi_send(8'hA5);
        if (dut.rx_data !== 8'hA5 || led !== 8'hA5) $fatal(1, "rx_data=%02X led=%02X", dut.rx_data, led);
        #70000;
        $display("PASS spi_rx view: 0x55, 0xA5 received at 8th rising edge");
        $finish;
    end
endmodule
