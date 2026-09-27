`timescale 1ns/1ps
// Simple UART transmitter: 8N1, LSB first, idle high. One start bit,
// eight data bits, one stop bit, each held for CLKS_PER_BIT clocks.
// A one-cycle tx_start pulse (only valid while busy is low) latches
// tx_data and begins the frame.
module uart_tx #(
    parameter integer CLKS_PER_BIT = 5208
) (
    input  wire       clk,
    input  wire       tx_start,
    input  wire [7:0] tx_data,
    output reg         tx   = 1'b1,
    output reg         busy = 1'b0
);
    localparam integer CNT_W = $clog2(CLKS_PER_BIT + 1);

    localparam [1:0] S_IDLE = 2'd0,
                      S_START = 2'd1,
                      S_DATA  = 2'd2,
                      S_STOP  = 2'd3;

    reg [1:0]       state   = S_IDLE;
    reg [CNT_W-1:0] clk_cnt = {CNT_W{1'b0}};
    reg [2:0]       bit_idx = 3'd0;
    reg [7:0]       data_reg = 8'h00;

    always @(posedge clk) begin
        case (state)
            S_IDLE: begin
                tx      <= 1'b1;
                busy    <= 1'b0;
                clk_cnt <= {CNT_W{1'b0}};
                bit_idx <= 3'd0;
                if (tx_start) begin
                    data_reg <= tx_data;
                    busy     <= 1'b1;
                    state    <= S_START;
                end
            end

            S_START: begin
                tx <= 1'b0;
                if (clk_cnt == CLKS_PER_BIT - 1) begin
                    clk_cnt <= {CNT_W{1'b0}};
                    state   <= S_DATA;
                end else begin
                    clk_cnt <= clk_cnt + 1'b1;
                end
            end

            S_DATA: begin
                tx <= data_reg[bit_idx];
                if (clk_cnt == CLKS_PER_BIT - 1) begin
                    clk_cnt <= {CNT_W{1'b0}};
                    if (bit_idx == 3'd7) begin
                        bit_idx <= 3'd0;
                        state   <= S_STOP;
                    end else begin
                        bit_idx <= bit_idx + 1'b1;
                    end
                end else begin
                    clk_cnt <= clk_cnt + 1'b1;
                end
            end

            S_STOP: begin
                tx <= 1'b1;
                if (clk_cnt == CLKS_PER_BIT - 1) begin
                    clk_cnt <= {CNT_W{1'b0}};
                    busy    <= 1'b0;
                    state   <= S_IDLE;
                end else begin
                    clk_cnt <= clk_cnt + 1'b1;
                end
            end

            default: state <= S_IDLE;
        endcase
    end
endmodule
