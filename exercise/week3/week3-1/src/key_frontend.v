`timescale 1ns/1ps
// Twelve independent push-key inputs. Each bit gets its own 2-FF
// synchronizer, a majority-free counter debouncer (~10 ms default at
// 50 MHz) and a rising-edge one-shot, so holding a key produces exactly
// one pulse on key_pulse. There is no board reset button; every register
// below starts from its declared initial value (Xilinx FPGAs support
// initial values on flip-flops).
module key_frontend #(
    parameter integer DEBOUNCE_CYCLES = 500_000
) (
    input  wire        clk,
    input  wire [11:0] keys,
    output wire [11:0] key_pulse
);
    localparam integer CNT_W = $clog2(DEBOUNCE_CYCLES + 1);

    genvar i;
    generate
        for (i = 0; i < 12; i = i + 1) begin : g_key
            reg [1:0]        sync_ff    = 2'b00;
            reg              debounced  = 1'b0;
            reg              debounced_d = 1'b0;
            reg [CNT_W-1:0]  stable_cnt = {CNT_W{1'b0}};

            always @(posedge clk)
                sync_ff <= {sync_ff[0], keys[i]};

            // Count consecutive clocks where the synchronized input differs
            // from the currently accepted (debounced) value; commit it once
            // the input has been stable for DEBOUNCE_CYCLES clocks.
            always @(posedge clk) begin
                if (sync_ff[1] != debounced) begin
                    if (stable_cnt == DEBOUNCE_CYCLES - 1) begin
                        debounced  <= sync_ff[1];
                        stable_cnt <= {CNT_W{1'b0}};
                    end else begin
                        stable_cnt <= stable_cnt + 1'b1;
                    end
                end else begin
                    stable_cnt <= {CNT_W{1'b0}};
                end
            end

            always @(posedge clk)
                debounced_d <= debounced;

            assign key_pulse[i] = debounced & ~debounced_d;
        end
    endgenerate
endmodule
