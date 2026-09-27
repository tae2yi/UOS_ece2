`timescale 1ns/1ps
// Reaction game controller. One core clock is one millisecond on the board.
// Adapted from exercise/week3/src/reaction_core.v: the display/result/counter
// width is narrowed from 27 bits (8-digit, seg7 display) to 17 bits, and the
// saturation value is lowered from 99999999 to 99999, since this project's
// 16x2 character LCD only shows a 5-digit millisecond value.
module reaction_core #(
    parameter integer MIN_DELAY_MS = 1000,
    parameter integer MAX_DELAY_MS = 10000
) (
    input  wire        clk,
    input  wire        rst,
    input  wire        press,
    output reg         led_on,
    output reg  [16:0] display_ms,
    output reg  [2:0]  state
);
    localparam [2:0] READY = 3'd0;
    localparam [2:0] WAITING = 3'd1;
    localparam [2:0] REACTING = 3'd2;
    localparam [2:0] HOLD = 3'd3;

    localparam [16:0] MAX_DISPLAY_MS = 17'd99999;
    localparam integer EFFECTIVE_MIN_DELAY_MS =
        (MIN_DELAY_MS < 1) ? 1 : MIN_DELAY_MS;
    localparam integer EFFECTIVE_MAX_DELAY_MS =
        (MAX_DELAY_MS < EFFECTIVE_MIN_DELAY_MS) ?
        EFFECTIVE_MIN_DELAY_MS : MAX_DELAY_MS;
    localparam integer DELAY_RANGE_MS =
        EFFECTIVE_MAX_DELAY_MS - EFFECTIVE_MIN_DELAY_MS + 1;

    reg [15:0] lfsr;
    reg [31:0] wait_target;
    reg [31:0] wait_count;
    reg [16:0] reaction_count;
    reg [16:0] result_ms;

    wire lfsr_feedback = lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10];
    wire [15:0] lfsr_next = {lfsr[14:0], lfsr_feedback};
    wire [31:0] sampled_delay =
        EFFECTIVE_MIN_DELAY_MS + (lfsr % DELAY_RANGE_MS);

    always @(posedge clk) begin
        if (rst) begin
            lfsr <= 16'h1ACE;
        end else begin
            // Free-running nonzero LFSR: its value at a button press varies
            // with the time at which the player starts each round.
            lfsr <= lfsr_next;
        end
    end

    always @(posedge clk) begin
        if (rst) begin
            state <= READY;
            led_on <= 1'b1;
            wait_target <= 32'd1;
            wait_count <= 32'd0;
            reaction_count <= 17'd0;
            result_ms <= 17'd0;
            display_ms <= 17'd0;
        end else begin
            case (state)
                READY, HOLD: begin
                    led_on <= 1'b1;
                    display_ms <= result_ms;
                    if (press) begin
                        wait_target <= sampled_delay;
                        wait_count <= 32'd0;
                        reaction_count <= 17'd0;
                        result_ms <= 17'd0;
                        display_ms <= 17'd0;
                        led_on <= 1'b0;
                        state <= WAITING;
                    end
                end

                WAITING: begin
                    // Early presses are ignored. The player must wait until
                    // the LED turns on, then press again to stop the timer.
                    led_on <= 1'b0;
                    display_ms <= 17'd0;
                    if (wait_count + 1 >= wait_target) begin
                        wait_count <= wait_count + 1'b1;
                        reaction_count <= 17'd0;
                        led_on <= 1'b1;
                        state <= REACTING;
                    end else begin
                        wait_count <= wait_count + 1'b1;
                    end
                end

                REACTING: begin
                    led_on <= 1'b1;
                    if (press) begin
                        // Cycle table from the LED-on edge C0:
                        //   C0: count=0; on Cn, the old count is n-1.
                        // Include the interval ending on this edge so a press
                        // consumed at Cn records exactly n milliseconds.
                        if (reaction_count < MAX_DISPLAY_MS)
                            result_ms <= reaction_count + 1'b1;
                        else
                            result_ms <= MAX_DISPLAY_MS;
                        if (reaction_count < MAX_DISPLAY_MS)
                            display_ms <= reaction_count + 1'b1;
                        else
                            display_ms <= MAX_DISPLAY_MS;
                        state <= HOLD;
                    end else begin
                        // Do not reveal a running time. The requirement is to
                        // show the reaction result immediately after the
                        // player's second press, so keep the display at zero
                        // while the LED is on and the timer is running.
                        display_ms <= 17'd0;
                        if (reaction_count < MAX_DISPLAY_MS) begin
                            reaction_count <= reaction_count + 1'b1;
                        end
                    end
                end

                default: begin
                    state <= READY;
                    led_on <= 1'b1;
                    wait_target <= 32'd1;
                    wait_count <= 32'd0;
                    reaction_count <= 17'd0;
                    result_ms <= 17'd0;
                    display_ms <= 17'd0;
                end
            endcase
        end
    end
endmodule
