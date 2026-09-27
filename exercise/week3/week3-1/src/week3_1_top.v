`timescale 1ns/1ps
// Combo II-DLD S75 top. B6 is the 50 MHz trainer clock. There is no
// board reset button (K4/N8 are keypad keys); every stateful register
// in this design starts from its declared initial value instead.
//
// keys[11:0] bit order (matches constraints/week3_1_top.xdc):
//   0=key_1 1=key_2 2=key_3 3=key_4 4=key_5 5=key_6
//   6=key_7 7=key_8 8=key_9 9=key_0 10=key_star 11=key_sharp
module week3_1_top #(
    parameter integer N_MAX            = 9,
    parameter integer DEBOUNCE_CYCLES  = 500_000,
    parameter integer SCAN_TICK_CYCLES = 50_000,
    parameter integer CLKS_PER_BIT     = 5208,
    parameter integer MAX_DIGITS       = 10
) (
    input  wire        clk,       // B6, 50 MHz
    input  wire [11:0] keys,      // active-high push keys
    output wire         bdio0,     // F8, 50 MHz / 2^N
    output wire         bdio2,     // A7, UART TX
    output wire [7:0]  seg_data,
    output wire [7:0]  seg_com
);
    localparam KEY_1     = 0,  KEY_2 = 1,  KEY_3 = 2,  KEY_4 = 3,
               KEY_5     = 4,  KEY_6 = 5,  KEY_7 = 6,  KEY_8 = 7,
               KEY_9     = 8,  KEY_0 = 9,  KEY_STAR = 10, KEY_SHARP = 11;

    wire [11:0] key_pulse;

    key_frontend #(
        .DEBOUNCE_CYCLES(DEBOUNCE_CYCLES)
    ) u_key_frontend (
        .clk       (clk),
        .keys      (keys),
        .key_pulse (key_pulse)
    );

    // --- '#' : division exponent N, wraps 0..N_MAX, power-up N=0 -----
    reg [3:0] n_reg = 4'd0;
    always @(posedge clk)
        if (key_pulse[KEY_SHARP])
            n_reg <= (n_reg == N_MAX) ? 4'd0 : n_reg + 1'b1;

    clk_out_oddr u_clk_out (
        .clk     (clk),
        .n_sel   (n_reg),
        .clk_out (bdio0)
    );

    // --- digit entry + '*' send ---------------------------------------
    wire [9:0] digit_pulse = { key_pulse[KEY_9], key_pulse[KEY_8],
                                key_pulse[KEY_7], key_pulse[KEY_6],
                                key_pulse[KEY_5], key_pulse[KEY_4],
                                key_pulse[KEY_3], key_pulse[KEY_2],
                                key_pulse[KEY_1], key_pulse[KEY_0] };

    wire       tx_busy;
    wire       tx_start;
    wire [7:0] tx_data;
    wire [3:0] digit_count;
    wire [39:0] digits_flat;

    id_buffer #(
        .MAX_DIGITS(MAX_DIGITS)
    ) u_id_buffer (
        .clk         (clk),
        .digit_pulse (digit_pulse),
        .star_pulse  (key_pulse[KEY_STAR]),
        .tx_busy     (tx_busy),
        .tx_start    (tx_start),
        .tx_data     (tx_data),
        .digit_count (digit_count),
        .digits_flat (digits_flat)
    );

    uart_tx #(
        .CLKS_PER_BIT(CLKS_PER_BIT)
    ) u_uart_tx (
        .clk      (clk),
        .tx_start (tx_start),
        .tx_data  (tx_data),
        .tx       (bdio2),
        .busy     (tx_busy)
    );

    // --- display: digits 7..6 = N (two decimal digits), digits 5..0 = --
    // --- last 6 entered digits, right-aligned, newest at digit 0 -------
    wire [3:0] recent_digit [0:5];
    genvar gi;
    generate
        for (gi = 0; gi < 6; gi = gi + 1) begin : g_recent
            wire signed [5:0] src_idx = $signed({1'b0, digit_count}) - 1 - gi;
            assign recent_digit[gi] = (src_idx >= 0) ?
                digits_flat[src_idx*4 +: 4] : 4'hF;
        end
    endgenerate

    wire [31:0] digit_codes = { 4'd0, n_reg,
                                 recent_digit[5], recent_digit[4],
                                 recent_digit[3], recent_digit[2],
                                 recent_digit[1], recent_digit[0] };

    seg7_scan8 #(
        .SCAN_TICK_CYCLES(SCAN_TICK_CYCLES)
    ) u_seg7 (
        .clk         (clk),
        .digit_codes (digit_codes),
        .seg_data    (seg_data),
        .seg_com     (seg_com)
    );
endmodule
