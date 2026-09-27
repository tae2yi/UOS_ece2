`timescale 1ns/1ps
// HD44780-style 16x2 character LCD driver, 8-bit write-only bus.
// Same 4-phase byte-write timing and init/refresh sequence as the course's
// lcd_lab2_modes reference driver. The board's main clock is 1 kHz
// (1 clock = 1 ms), so every phase already satisfies the LCD's E-pulse and
// command recovery timing without extra counters.
module lcd_reaction #(
    parameter integer POWER_WAIT = 50
) (
    input  wire        clk,
    input  wire        rst,
    input  wire [2:0]  state,       // reaction_core state: 0 READY,1 WAITING,2 REACTING,3 HOLD
    input  wire [19:0] bcd_digits,  // five packed BCD digits of the measured ms (digit0=units)
    output reg          lcd_e,
    output reg          lcd_rs,
    output wire         lcd_rw,
    output reg  [7:0]   lcd_data
);
    localparam [2:0] READY    = 3'd0;
    localparam [2:0] WAITING  = 3'd1;
    localparam [2:0] REACTING = 3'd2;
    localparam [2:0] HOLD     = 3'd3;

    reg [1:0] phase;
    integer power_count;
    reg [5:0] index;
    reg [2:0] shown_state;
    reg [19:0] shown_bcd;
    reg [127:0] line1;
    reg [127:0] line2;

    assign lcd_rw = 1'b0;

    // Line text is derived from the state/value latched at index==5, the
    // moment the 0x80 (line-1 address) byte is sent, so one full refresh
    // shows a single consistent snapshot instead of a screen that changes
    // mid-refresh.
    always @* begin
        case (shown_state)
            READY:    line1 = "PRESS N8 TO GO  ";
            WAITING:  line1 = "WAIT...         ";
            REACTING: line1 = "GO! PRESS N8    ";
            default:  line1 = "REACTION TIME   "; // HOLD
        endcase
        if (shown_state == HOLD) begin
            line2 = {"TIME: ",
                     8'h30 + shown_bcd[19:16], // ten-thousands
                     8'h30 + shown_bcd[15:12], // thousands
                     8'h30 + shown_bcd[11:8],  // hundreds
                     8'h30 + shown_bcd[7:4],   // tens
                     8'h30 + shown_bcd[3:0],   // units
                     " ms  "};
        end else begin
            line2 = {16{8'h20}};
        end
    end

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            phase <= 2'd0;
            power_count <= 0;
            index <= 6'd0;
            shown_state <= READY;
            shown_bcd <= 20'd0;
            lcd_e <= 1'b0;
            lcd_rs <= 1'b0;
            lcd_data <= 8'h00;
        end else if (power_count < POWER_WAIT) begin
            power_count <= power_count + 1;
        end else begin
            case (phase)
                2'd0: begin
                    lcd_e <= 1'b0;
                    lcd_rs <= 1'b0;
                    case (index)
                        6'd0, 6'd1, 6'd2: lcd_data <= 8'h38; // function set x3
                        6'd3: lcd_data <= 8'h0c;             // display on, cursor off
                        6'd4: lcd_data <= 8'h06;             // entry mode, increment
                        6'd5: begin
                            lcd_data <= 8'h80;               // line 1 DDRAM address
                            shown_state <= state;
                            shown_bcd <= bcd_digits;
                        end
                        6'd22: lcd_data <= 8'hc0;            // line 2 DDRAM address
                        default: begin
                            lcd_rs <= 1'b1;
                            if (index >= 6'd6 && index <= 6'd21)
                                lcd_data <= line1[127-(index-6)*8 -: 8];
                            else if (index >= 6'd23 && index <= 6'd38)
                                lcd_data <= line2[127-(index-23)*8 -: 8];
                            else
                                lcd_data <= 8'h20;
                        end
                    endcase
                    phase <= 2'd1;
                end
                2'd1: begin
                    lcd_e <= 1'b1;
                    phase <= 2'd2;
                end
                2'd2: begin
                    lcd_e <= 1'b0;
                    phase <= 2'd3;
                end
                2'd3: begin
                    // First function-set recovery is 6 ms including setup of
                    // the next byte.
                    if (index == 6'd0 && power_count < POWER_WAIT + 2) begin
                        power_count <= power_count + 1;
                    end else begin
                        phase <= 2'd0;
                        index <= (index == 6'd38) ? 6'd5 : index + 1'b1;
                    end
                end
            endcase
        end
    end
endmodule
