`timescale 1ns/1ps
// SRAM 버스는 읽을 때 FPGA가 구동하지 않고 Z 상태로 놓습니다.
// ctrl_w와 ctrl_r가 동시에 들어오면 둘 다 수행하지 않습니다.
module sram_bus_control(
    input wire ctrl_w,ctrl_r,
    output wire drive_data,read_data,
    output wire ram_cs,ram_oe,ram_we
);
    assign drive_data=ctrl_w && !ctrl_r;
    assign read_data=ctrl_r && !ctrl_w;
    assign ram_cs=!(drive_data || read_data);
    assign ram_oe=!read_data;
    assign ram_we=!drive_data;
endmodule
