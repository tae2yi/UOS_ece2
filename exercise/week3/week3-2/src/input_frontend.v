`timescale 1ns/1ps
// Synchronize the asynchronous board button and emit a one-cycle pulse on the
// first synchronized rising edge. Rearm only after a stable synchronized-low
// interval. The main clock is 1 kHz.
module input_frontend #(
    parameter integer RELEASE_STABLE_CYCLES = 5
) (
    input  wire clk,
    input  wire rst,
    input  wire button,
    output wire reset,
    output wire press
);
    (* ASYNC_REG = "TRUE" *) reg [1:0] reset_pipe;
    (* ASYNC_REG = "TRUE" *) reg button_meta;
    (* ASYNC_REG = "TRUE" *) reg button_sync;

    // Keep the release interval well-defined for a zero/negative override.
    localparam integer EFFECTIVE_RELEASE_CYCLES =
        (RELEASE_STABLE_CYCLES < 1) ? 1 : RELEASE_STABLE_CYCLES;
    localparam integer COUNT_WIDTH = (EFFECTIVE_RELEASE_CYCLES < 2) ? 1 :
                                     $clog2(EFFECTIVE_RELEASE_CYCLES + 1);
    reg [COUNT_WIDTH-1:0] release_count;
    reg button_sync_d;
    reg armed;

    assign reset = reset_pipe[1];

    // Assert reset immediately; release it synchronously after two clock edges.
    always @(posedge clk or posedge rst) begin
        if (rst)
            reset_pipe <= 2'b11;
        else
            reset_pipe <= {reset_pipe[0], 1'b0};
    end

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            button_meta <= 1'b0;
            button_sync <= 1'b0;
            button_sync_d <= 1'b0;
        end else begin
            button_meta <= button;
            button_sync <= button_meta;
            button_sync_d <= button_sync;
        end
    end

    // The pulse follows the first rising transition of the synchronized
    // button. It remains high for one clock period; the core consumes it on
    // the next rising edge. There is deliberately no high-level debounce.
    assign press = armed && button_sync && !button_sync_d;

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            release_count <= {COUNT_WIDTH{1'b0}};
            armed <= 1'b1;
        end else if (press) begin
            armed <= 1'b0;
            release_count <= {COUNT_WIDTH{1'b0}};
        end else if (armed) begin
            release_count <= {COUNT_WIDTH{1'b0}};
        end else if (!button_sync) begin
            if (release_count == EFFECTIVE_RELEASE_CYCLES - 1) begin
                armed <= 1'b1;
                release_count <= {COUNT_WIDTH{1'b0}};
            end else begin
                release_count <= release_count + 1'b1;
            end
        end else begin
            release_count <= {COUNT_WIDTH{1'b0}};
        end
    end
endmodule
