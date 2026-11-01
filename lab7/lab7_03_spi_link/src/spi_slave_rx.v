`timescale 1ns/1ps
// SPI 슬레이브 수신 (Mode 0, 8비트, MSB 먼저, MISO 없음) — STM32_3 과제10
// 1) 비동기 입력 SCK·MOSI·CS_n을 2단 플립플롭으로 50 MHz 클록에 맞춘다(메타안정 방지).
// 2) 동기화한 SCK의 이전 값과 현재 값을 비교해 상승 에지(0 -> 1)를 한 클록 펄스로 만든다.
// 3) CS_n이 LOW인 동안 상승 에지마다 MOSI를 시프트 레지스터 오른쪽에 넣는다(먼저 온 비트가 MSB로 밀려 올라감).
// 4) 8번째 에지에서 바이트를 data에 내고 valid를 한 클록 1로 만든다.
// 5) CS_n이 HIGH가 되면 비트 카운터를 0으로 돌려, 중간에 끊긴 바이트가 다음 바이트에 섞이지 않게 한다.
// SCK 781.25 kHz(MCU 기본)면 반주기 640 ns = 32클록이라 2클록 동기화 지연은 충분히 작다.
// MOSI와 SCK가 같은 2단 지연을 거치므로 에지 시점의 MOSI 값을 그대로 읽는다(MOSI는 하강 에지에서만 바뀐다).
module spi_slave_rx (
    input  wire clk,
    input  wire rst_p,
    input  wire sck,
    input  wire mosi,
    input  wire cs_n,
    output reg  [7:0] data,
    output reg  valid,
    output wire [2:0] bit_count_o,   // 파형 확인용
    output wire sck_rise_o           // 파형 확인용
);
    (* ASYNC_REG = "TRUE" *) reg [1:0] sck_sync;
    (* ASYNC_REG = "TRUE" *) reg [1:0] mosi_sync;
    (* ASYNC_REG = "TRUE" *) reg [1:0] cs_sync;
    reg sck_prev;
    reg [6:0] shift;
    reg [2:0] bit_count;

    wire sck_s  = sck_sync[1];
    wire mosi_s = mosi_sync[1];
    wire cs_n_s = cs_sync[1];
    wire sck_rise = sck_s & ~sck_prev;

    assign bit_count_o = bit_count;
    assign sck_rise_o = sck_rise;

    always @(posedge clk) begin
        if (rst_p) begin
            sck_sync <= 2'b00; mosi_sync <= 2'b00; cs_sync <= 2'b11;
            sck_prev <= 0; shift <= 0; bit_count <= 0;
            data <= 0; valid <= 0;
        end else begin
            sck_sync  <= {sck_sync[0], sck};
            mosi_sync <= {mosi_sync[0], mosi};
            cs_sync   <= {cs_sync[0], cs_n};
            sck_prev  <= sck_s;
            valid <= 0;
            if (cs_n_s) begin
                bit_count <= 0;   // CS 해제: 처음부터
            end else if (sck_rise) begin
                if (bit_count == 3'd7) begin
                    data <= {shift, mosi_s};  // 8번째 비트
                    valid <= 1;
                    bit_count <= 0;
                end else begin
                    shift <= {shift[5:0], mosi_s};
                    bit_count <= bit_count + 1'b1;
                end
            end
        end
    end
endmodule
