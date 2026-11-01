`timescale 1ns/1ps
// SPI 마스터 송신 (Mode 0, 8비트, MSB 먼저, MISO 없음) — STM32_3 과제11
// SCK = CLK_HZ / (2 * HALF) . 50 MHz, HALF = 50이면 500 kHz(주기 2 us)로 매뉴얼의 1 MHz 이하 조건을 만족한다.
// 순서(반주기 = HALF 클록):
//   LEAD : CS_n LOW, MOSI = bit7 준비, 반주기 기다림         ← 첫 비트를 첫 상승 에지 전에 준비
//   HIGH : SCK 1 (수신 측이 이 상승 에지에서 읽음), 반주기
//   LOW  : SCK 0, 이 하강 에지에서 MOSI를 다음 비트로 바꿈, 반주기 → HIGH ... 8번 반복
//   TRAIL: 8번째 하강 에지 뒤 반주기 기다렸다가 CS_n HIGH
//   GAP  : CS_n HIGH를 반주기 이상 유지한 뒤 done
// 모든 출력은 플립플롭에서 바로 나가 글리치가 없다. SCK는 대기 중 LOW.
module spi_master_tx #(
    parameter integer HALF = 50
) (
    input  wire clk,
    input  wire rst_p,
    input  wire start,
    input  wire [7:0] data,
    output reg  sck,
    output reg  mosi,
    output reg  cs_n,
    output wire busy,
    output reg  done
);
    localparam [2:0] IDLE = 3'd0, LEAD = 3'd1, HIGH = 3'd2, LOW = 3'd3, TRAIL = 3'd4, GAP = 3'd5;
    reg [2:0] state;
    reg [7:0] shift;
    reg [2:0] bit_index;              // 지금 내보낸 비트 순번 0(bit7) ~ 7(bit0)
    reg [$clog2(HALF+1)-1:0] count;
    wire tick = (count == 0);

    assign busy = (state != IDLE);

    always @(posedge clk) begin
        if (rst_p) begin
            state <= IDLE; shift <= 0; bit_index <= 0; count <= 0;
            sck <= 0; mosi <= 0; cs_n <= 1; done <= 0;
        end else begin
            done <= 0;
            if (state != IDLE && !tick) count <= count - 1'b1;
            case (state)
                IDLE: if (start) begin
                    shift <= data; mosi <= data[7]; cs_n <= 0;
                    bit_index <= 0; count <= HALF - 1; state <= LEAD;
                end
                LEAD: if (tick) begin
                    sck <= 1; count <= HALF - 1; state <= HIGH;
                end
                HIGH: if (tick) begin
                    sck <= 0; count <= HALF - 1;
                    if (bit_index == 3'd7) state <= TRAIL;
                    else begin
                        shift <= {shift[6:0], 1'b0};
                        mosi <= shift[6];  // 다음 비트
                        bit_index <= bit_index + 1'b1;
                        state <= LOW;
                    end
                end
                LOW: if (tick) begin
                    sck <= 1; count <= HALF - 1; state <= HIGH;
                end
                TRAIL: if (tick) begin
                    cs_n <= 1; mosi <= 0;
                    count <= HALF - 1; state <= GAP;
                end
                GAP: if (tick) begin
                    done <= 1; state <= IDLE;
                end
                default: state <= IDLE;
            endcase
        end
    end
endmodule
