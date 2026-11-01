`timescale 1ns/1ps
// STM32_3 과제11 TB: FPGA 마스터 송신 → (MCU 슬레이브)
// 송신 간격만 1 s 대신 10 ms(PERIOD_CLKS = 500,000)로 줄이고 SCK 500 kHz, UART 9600은 보드와 같다.
// TB 안의 SPI 수신 모델(오실로스코프 + MCU 슬레이브 역할)이 매 바이트마다 확인한다:
//   (1) CS_n LOW 동안 SCK 상승 에지가 정확히 8번, SCK 대기 LOW
//   (2) SCK 주기 2000 ns(500 kHz, 1 MHz 이하), CS_n LOW → 첫 상승 에지 1000 ns
//   (3) MOSI는 SCK가 LOW일 때만 바뀐다(상승 에지 전에 준비, 하강 에지에서 변경)
//   (4) 상승 에지에서 읽은 8비트(MSB 먼저) = 0x55, 0xA5, 0x00, 0xFF 반복
//   (5) FPGA UART 출력 "TX=<값>\r\n"
// 읽은 바이트는 sim/fpga_tx_bytes.hex에 적어 MCU 슬레이브 호스트 시뮬레이션(stm32_3_hostsim)의 입력으로 쓴다.
module tb;
    localparam integer NBYTES = 8;
    localparam integer BIT_NS = 5208 * 20;
    reg clk = 0, rst = 1;
    always #10 clk = ~clk;
    wire sck, mosi, cs_n, txd;
    wire [7:0] led;
    spi_tx_uart #(.PERIOD_CLKS(500_000)) dut(
        .clk_50mhz(clk), .rst_p(rst), .spi_sck(sck), .spi_mosi(mosi), .spi_cs_n(cs_n),
        .uart_txd(txd), .led(led));

    function [7:0] pattern(input integer i);
        case (i % 4)
            0: pattern = 8'h55;
            1: pattern = 8'hA5;
            2: pattern = 8'h00;
            default: pattern = 8'hFF;
        endcase
    endfunction
    function [7:0] hex(input [3:0] v);
        hex = v < 10 ? 8'h30 + v : 8'h37 + v;
    endfunction

    integer errors = 0, n_bytes = 0, n_lines = 0, edges = 0, fd;
    realtime t_cs, t_rise, t_prev_rise, t_cs_high;
    reg [7:0] got;

    // (3) MOSI가 SCK HIGH 동안 바뀌면 오류
    //     하강 에지와 같은 클록에 바뀌는 것은 정상이므로 1 ns 뒤에도 SCK가 HIGH인지 본다.
    always @(mosi) if (!cs_n) #1 if (sck) begin
        $display("FAIL MOSI changed while SCK high at %0.1f ns", $realtime); errors = errors + 1;
    end
    always @(negedge cs_n) begin
        t_cs = $realtime; edges = 0; got = 0;
        if (sck !== 1'b0) begin $display("FAIL SCK not idle low at CS fall"); errors = errors + 1; end
        if (n_bytes > 0 && t_cs - t_cs_high < 1000) begin $display("FAIL CS high too short"); errors = errors + 1; end
    end
    always @(posedge sck) begin
        if (cs_n) begin $display("FAIL SCK edge while CS high"); errors = errors + 1; end
        t_rise = $realtime;
        if (edges == 0 && (t_rise - t_cs) != 1000) begin
            $display("FAIL CS->first edge %0.1f ns", t_rise - t_cs); errors = errors + 1;
        end
        if (edges > 0 && (t_rise - t_prev_rise) != 2000) begin
            $display("FAIL SCK period %0.1f ns", t_rise - t_prev_rise); errors = errors + 1;
        end
        t_prev_rise = t_rise;
        got = {got[6:0], mosi};
        edges = edges + 1;
    end
    always @(posedge cs_n) if (!rst && n_bytes < NBYTES) begin
        t_cs_high = $realtime;
        if (edges != 8 || got !== pattern(n_bytes)) begin
            $display("FAIL byte %0d: %0d edges, got %02X want %02X", n_bytes, edges, got, pattern(n_bytes));
            errors = errors + 1;
        end else
            $display("t=%7.3f ms  SPI byte %0d: %02X (8 edges, period 2000 ns, CS->SCK 1000 ns)",
                     t_cs/1e6, n_bytes, got);
        $fdisplay(fd, "%02x", got);
        n_bytes = n_bytes + 1;
    end

    // (5) PC 쪽 UART 수신
    reg [7:0] line [0:15];
    integer len = 0;
    initial begin : uart_monitor
        reg [7:0] ch, want;
        integer b;
        forever begin
            @(negedge txd);
            #(BIT_NS + BIT_NS/2);
            for (b = 0; b < 8; b = b + 1) begin ch[b] = txd; #(BIT_NS); end
            line[len] = ch; len = len + 1;
            if (ch == 8'h0A) begin
                want = pattern(n_lines);
                if (len != 7 || line[0] != "T" || line[1] != "X" || line[2] != "=" ||
                    line[3] != hex(want[7:4]) || line[4] != hex(want[3:0]) || line[5] != 8'h0D) begin
                    $display("FAIL UART line %0d", n_lines); errors = errors + 1;
                end
                if (led !== want) begin $display("FAIL led=%02X", led); errors = errors + 1; end
                n_lines = n_lines + 1; len = 0;
            end
        end
    end

    initial begin
        fd = $fopen("sim/fpga_tx_bytes.hex", "w");
        repeat (5) @(posedge clk); rst = 0;
        wait (n_lines == NBYTES);
        #1000;
        $fclose(fd);
        if (errors == 0)
            $display("PASS spi_tx tb: %0d bytes 55 A5 00 FF x2, SCK 500 kHz, Mode 0 timing, UART TX= lines match", n_bytes);
        else
            $fatal(1, "spi_tx tb: %0d errors", errors);
        $finish;
    end
endmodule
