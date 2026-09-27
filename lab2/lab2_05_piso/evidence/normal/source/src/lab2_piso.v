`timescale 1ns/1ps
// Combo II-DLD S75. Main clock B6 must be set to 1 kHz.
// K4: reset. N8: step button. DIP SW1..8 = sw[7]..sw[0].
module lab2_piso #(parameter integer STABLE_CYCLES = 20) (
    input wire clk, rst, button,
    input wire [7:0] sw,
    output wire [7:0] led
);

    wire reset, press;
    wire [7:0] switches;
    input_frontend #(.STABLE_CYCLES(STABLE_CYCLES)) inputs(
        clk, rst, button, sw, reset, press, switches);

    wire serial_out;
    wire [3:0] value;
    piso4 core(clk, reset, press && switches[0], press && !switches[0],
               switches[7:4], serial_out, value);
    assign led = {value, 3'b000, serial_out};
endmodule
