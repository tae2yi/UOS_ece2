`timescale 1ns/1ps
module sram(
    input wire ctrl_w,ctrl_r,
    input wire [3:0] address,data_in,
    output wire ram_cs,ram_oe,ram_we,
    output wire [17:0] ram_address,
    inout wire [15:0] ram_data,
    output wire [7:0] led_out
);
    wire drive_data,read_data;
    sram_bus_control u_control(ctrl_w,ctrl_r,drive_data,read_data,ram_cs,ram_oe,ram_we);
    assign ram_address={14'b0,address};
    assign ram_data=drive_data ? {12'b0,data_in} : 16'bz;
    assign led_out=read_data ? {4'b0,ram_data[3:0]} : 8'b0;
endmodule
