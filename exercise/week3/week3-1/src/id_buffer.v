`timescale 1ns/1ps
// Digit entry buffer and '*' send sequencer. Digit key one-shots append
// to a 10-entry buffer (extra digits beyond MAX_DIGITS are dropped). A
// '*' one-shot transmits the stored digits, in entry order, as ASCII
// over uart_tx, then clears the buffer; '*' on an empty buffer does
// nothing. Digit and '*' keys are ignored while a send is in progress
// (only the S_IDLE state samples them). If two digit keys pulse in the
// exact same clock (a rare simultaneous double-press), only the
// numerically highest digit is appended, since it is the last write in
// program order to the same buffer slot; this is considered acceptable
// for a hand-operated keypad.
module id_buffer #(
    parameter integer MAX_DIGITS = 10
) (
    input  wire        clk,
    input  wire [9:0]  digit_pulse,   // one-shot per digit key, bit N = digit N
    input  wire        star_pulse,    // one-shot for '*'
    input  wire        tx_busy,
    output reg         tx_start    = 1'b0,
    output reg  [7:0]  tx_data     = 8'h00,
    output reg  [3:0]  digit_count = 4'd0,
    output wire [39:0] digits_flat    // 10 x 4-bit BCD digits, index 0 = first entered
);
    localparam [1:0] S_IDLE      = 2'd0,
                      S_LOAD      = 2'd1,
                      S_WAIT_BUSY = 2'd2,
                      S_WAIT_DONE = 2'd3;

    reg [1:0] state      = S_IDLE;
    reg [3:0] send_index = 4'd0;

    reg [3:0] digit_mem [0:9];
    integer k;
    initial begin
        for (k = 0; k < 10; k = k + 1)
            digit_mem[k] = 4'd0;
    end

    genvar gi;
    generate
        for (gi = 0; gi < 10; gi = gi + 1) begin : g_flat
            assign digits_flat[gi*4 +: 4] = digit_mem[gi];
        end
    endgenerate

    integer d;
    always @(posedge clk) begin
        tx_start <= 1'b0;
        case (state)
            S_IDLE: begin
                if (star_pulse) begin
                    if (digit_count != 4'd0) begin
                        send_index <= 4'd0;
                        state      <= S_LOAD;
                    end
                end else begin
                    for (d = 0; d < 10; d = d + 1) begin
                        if (digit_pulse[d] && digit_count < MAX_DIGITS) begin
                            digit_mem[digit_count] <= d[3:0];
                            digit_count             <= digit_count + 1'b1;
                        end
                    end
                end
            end

            S_LOAD: begin
                tx_data  <= 8'h30 + {4'b0000, digit_mem[send_index]};
                tx_start <= 1'b1;
                state    <= S_WAIT_BUSY;
            end

            // Wait for uart_tx to register the start pulse (busy goes
            // high), then wait for the frame to finish (busy goes low)
            // before loading the next digit or closing out the send.
            S_WAIT_BUSY: begin
                if (tx_busy)
                    state <= S_WAIT_DONE;
            end

            S_WAIT_DONE: begin
                if (!tx_busy) begin
                    if (send_index == digit_count - 1'b1) begin
                        digit_count <= 4'd0;
                        state       <= S_IDLE;
                    end else begin
                        send_index <= send_index + 1'b1;
                        state      <= S_LOAD;
                    end
                end
            end

            default: state <= S_IDLE;
        endcase
    end
endmodule
