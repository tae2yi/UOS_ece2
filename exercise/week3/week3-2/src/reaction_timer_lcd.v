`timescale 1ns/1ps
// Combo II-DLD S75 top for the LCD reaction-time meter. B6 must be
// configured as a 1 kHz clock (1 clock = 1 ms).
module reaction_timer_lcd #(
    parameter integer RELEASE_STABLE_CYCLES = 5,
    parameter integer MIN_DELAY_MS = 1000,
    parameter integer MAX_DELAY_MS = 10000,
    parameter integer POWER_WAIT = 50
) (
    input  wire       clk,
    input  wire       rst,
    input  wire       button,
    output wire [7:0] led,
    output wire [7:0] lcd_data,
    output wire       lcd_e,
    output wire       lcd_rs,
    output wire       lcd_rw
);
    wire reset_sync;
    wire press;
    wire led_on;
    wire [16:0] display_ms;
    wire [2:0] state;
    wire [19:0] bcd_digits;

    input_frontend #(.RELEASE_STABLE_CYCLES(RELEASE_STABLE_CYCLES)) inputs (
        .clk(clk), .rst(rst), .button(button),
        .reset(reset_sync), .press(press)
    );

    reaction_core #(
        .MIN_DELAY_MS(MIN_DELAY_MS),
        .MAX_DELAY_MS(MAX_DELAY_MS)
    ) core (
        .clk(clk), .rst(reset_sync), .press(press),
        .led_on(led_on), .display_ms(display_ms), .state(state)
    );

    binary_to_bcd5 display_conversion (
        .binary_value(display_ms), .bcd_digits(bcd_digits)
    );

    lcd_reaction #(.POWER_WAIT(POWER_WAIT)) display_driver (
        .clk(clk), .rst(reset_sync), .state(state), .bcd_digits(bcd_digits),
        .lcd_e(lcd_e), .lcd_rs(lcd_rs), .lcd_rw(lcd_rw), .lcd_data(lcd_data)
    );

    // Only LED0 carries status; the remaining board LEDs are held off.
    assign led = {7'b0000000, led_on};
endmodule
