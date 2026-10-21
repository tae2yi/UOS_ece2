`timescale 1ns/1ps
module dac #(parameter UPDATE_CYCLES=500_000)(
    input wire clk_50mhz,rst_p,add_sel,
    output wire dac_csn,dac_ldacn,dac_wen,dac_a_b,
    output wire [7:0] dac_d,led_out
);
    wire [7:0] value;
    wire update;
    ramp8 #(.UPDATE_CYCLES(UPDATE_CYCLES)) u_ramp(clk_50mhz,rst_p,value,update);
    dac_parallel8 u_bus(clk_50mhz,rst_p,update,add_sel,value,
        dac_csn,dac_ldacn,dac_wen,dac_a_b,dac_d);
    assign led_out=dac_d;
endmodule
