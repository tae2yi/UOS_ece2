`timescale 1ns/1ps
module tb_reaction_timer_lcd;
    localparam [2:0] READY    = 3'd0;
    localparam [2:0] WAITING  = 3'd1;
    localparam [2:0] REACTING = 3'd2;
    localparam [2:0] HOLD     = 3'd3;

    reg clk = 1'b0;
    reg rst = 1'b1;
    reg button = 1'b0;
    wire [7:0] led;
    wire [7:0] lcd_data;
    wire lcd_e, lcd_rs, lcd_rw;

    integer checks = 0;
    integer cycle_count = 0;
    integer wait_entry_cycle = -1;
    integer go_cycle = -1;
    integer wait_entries = 0;
    integer last_press_sample_cycle = -1;
    reg [2:0] previous_state = 3'b111;

    // Each simulated clock edge represents one 1 ms board tick. Small
    // parameters keep the whole test fast.
    always #5 clk = ~clk;

    reaction_timer_lcd #(
        .RELEASE_STABLE_CYCLES(2),
        .MIN_DELAY_MS(1000),
        .MAX_DELAY_MS(10000),
        .POWER_WAIT(5)
    ) dut (
        .clk(clk), .rst(rst), .button(button),
        .led(led), .lcd_data(lcd_data),
        .lcd_e(lcd_e), .lcd_rs(lcd_rs), .lcd_rw(lcd_rw)
    );

    // Direct check of the BCD converter, independent of the core.
    reg [16:0] converter_input = 17'd0;
    wire [19:0] converter_output;
    binary_to_bcd5 converter_check (
        .binary_value(converter_input), .bcd_digits(converter_output)
    );

    // ---- LCD bus decode: track 0x80/0xC0 address bytes and the 16
    // character bytes that follow each, so the test reads back what the
    // display actually shows purely from the pin-level bus, with no
    // back-door access into the LCD driver's internals. ----
    reg [7:0] scr_line1 [0:15];
    reg [7:0] scr_line2 [0:15];
    integer col1 = 0;
    integer col2 = 0;
    reg cur_line = 1'b0;
    reg frame_ready = 1'b0;

    always @(negedge lcd_e) begin
        if (lcd_rs == 1'b0) begin
            if (lcd_data == 8'h80) begin
                cur_line = 1'b0;
                col1 = 0;
                frame_ready = 1'b0;
            end else if (lcd_data == 8'hc0) begin
                cur_line = 1'b1;
                col2 = 0;
            end
        end else begin
            if (cur_line == 1'b0 && col1 < 16) begin
                scr_line1[col1] = lcd_data;
                col1 = col1 + 1;
            end else if (cur_line == 1'b1 && col2 < 16) begin
                scr_line2[col2] = lcd_data;
                col2 = col2 + 1;
                if (col2 == 16)
                    frame_ready = 1'b1;
            end
        end
    end

    always @(posedge clk) begin
        cycle_count = cycle_count + 1;
        #1;
        if (dut.core.state == WAITING && previous_state != WAITING) begin
            wait_entry_cycle = cycle_count;
            wait_entries = wait_entries + 1;
        end
        if (dut.core.state == REACTING && previous_state == WAITING)
            go_cycle = cycle_count;
        previous_state = dut.core.state;
    end

    always @(negedge clk) begin
        if (!rst && dut.press)
            last_press_sample_cycle = cycle_count + 1;
    end

    task tick;
        begin
            @(posedge clk);
            #2;
        end
    endtask

    task check;
        input condition;
        input [8*120-1:0] description;
        begin
            checks = checks + 1;
            if (condition !== 1'b1) begin
                $display("LAB_FAIL %0s cycle=%0d", description, cycle_count);
                $fatal(1, "self-check failed");
            end
        end
    endtask

    task tap_button;
        begin
            @(negedge clk);
            button = 1'b1;
            wait (dut.press === 1'b1);
            @(posedge clk);
            #2;
            @(negedge clk);
            button = 1'b0;
            wait (dut.inputs.armed === 1'b1);
            #2;
        end
    endtask

    task wait_two_frames;
        begin
            @(posedge frame_ready);
            @(posedge frame_ready);
        end
    endtask

    function [127:0] expected_time_line;
        input integer ms_value;
        integer d0, d1, d2, d3, d4;
        begin
            d0 = ms_value % 10;
            d1 = (ms_value / 10) % 10;
            d2 = (ms_value / 100) % 10;
            d3 = (ms_value / 1000) % 10;
            d4 = (ms_value / 10000) % 10;
            expected_time_line = {"TIME: ",
                                   8'h30 + d4[3:0],
                                   8'h30 + d3[3:0],
                                   8'h30 + d2[3:0],
                                   8'h30 + d1[3:0],
                                   8'h30 + d0[3:0],
                                   " ms  "};
        end
    endfunction

    function [19:0] decimal_to_bcd5;
        input integer value;
        integer d;
        integer remaining;
        begin
            decimal_to_bcd5 = 20'd0;
            remaining = value;
            for (d = 0; d < 5; d = d + 1) begin
                decimal_to_bcd5[d*4 +: 4] = remaining % 10;
                remaining = remaining / 10;
            end
        end
    endfunction

    task check_line;
        input [127:0] expected;
        input use_line2;
        input [8*80-1:0] description;
        integer i;
        reg [7:0] exp_byte;
        reg [7:0] act_byte;
        begin
            for (i = 0; i < 16; i = i + 1) begin
                exp_byte = expected[127-i*8 -: 8];
                act_byte = use_line2 ? scr_line2[i] : scr_line1[i];
                checks = checks + 1;
                if (act_byte !== exp_byte) begin
                    $display("LAB_FAIL %0s col=%0d expected=%0d actual=%0d",
                             description, i, exp_byte, act_byte);
                    $fatal(1, "lcd text mismatch");
                end
            end
        end
    endtask

    integer expected_reaction;
    reg [31:0] first_sampled_delay;
    reg [31:0] second_sampled_delay;

    initial begin
        $dumpfile("wave.vcd");
        $dumpvars(0, tb_reaction_timer_lcd);
    end

    initial begin
        #200000;
        $fatal(1, "watchdog timeout");
    end

    initial begin
        // Reset: LED0 on, other LEDs off, LCD shows the ready screen.
        repeat (4) tick;
        check(led[0] === 1'b1, "reset leaves LED0 on");
        check(led[7:1] === 7'b0, "other LEDs remain off");
        check(dut.core.state === READY, "reset enters ready state");

        rst = 1'b0;
        repeat (4) tick;
        check(dut.reset_sync === 1'b0, "reset release is synchronized");

        wait_two_frames;
        check_line("PRESS N8 TO GO  ", 1'b0, "ready line1 text");
        check_line({16{8'h20}}, 1'b1, "ready line2 is blank");

        // Press N8: LED0 turns off and a random 1000..10000 ms wait starts.
        @(negedge clk);
        button = 1'b1;
        wait (dut.press === 1'b1);
        first_sampled_delay = dut.core.sampled_delay;
        @(posedge clk);
        #2;
        check(dut.core.state === WAITING, "first press starts a waiting round");
        check(first_sampled_delay >= 1000 && first_sampled_delay <= 10000,
              "sampled random delay is in 1000..10000 ms");
        check(led[0] === 1'b0, "LED0 turns off when a round starts");
        // Shorten the already-sampled wait so the test stays fast.
        dut.core.wait_target = 32'd20;
        @(negedge clk);
        button = 1'b0;
        wait (dut.inputs.armed === 1'b1);
        #2;

        wait_two_frames;
        check_line("WAIT...         ", 1'b0, "waiting line1 text");
        check_line({16{8'h20}}, 1'b1, "waiting line2 is blank");

        // A press while still waiting must be ignored.
        tap_button;
        check(dut.core.state === WAITING, "press during wait is ignored");
        check(led[0] === 1'b0, "early press does not turn LED on");

        while (dut.core.state !== REACTING)
            tick;
        check(led[0] === 1'b1, "LED0 turns on when the random delay expires");

        wait_two_frames;
        check_line("GO! PRESS N8    ", 1'b0, "reacting line1 text");
        check_line({16{8'h20}}, 1'b1, "reacting line2 is blank");

        // Wait a few ticks, then press to stop the timer.
        repeat (7) tick;
        tap_button;
        check(dut.core.state === HOLD, "press after LED turns on enters hold");
        check(led[0] === 1'b1, "LED stays on after stopping the timer");
        expected_reaction = last_press_sample_cycle - go_cycle;
        check(dut.display_ms === expected_reaction,
              "displayed reaction time matches the sampled response interval");
        check(dut.bcd_digits === decimal_to_bcd5(expected_reaction),
              "reaction result is converted to decimal BCD digits");

        wait_two_frames;
        check_line("REACTION TIME   ", 1'b0, "result line1 text");
        check_line(expected_time_line(expected_reaction), 1'b1,
                    "result line2 shows the measured ms value");

        // Hold keeps the round stopped with the result on screen.
        repeat (10) begin
            tick;
            check(dut.core.state === HOLD && led[0] === 1'b1,
                  "hold keeps the round stopped and LED on");
            check(dut.display_ms === expected_reaction,
                  "hold preserves the displayed reaction time");
        end

        // Pressing again in hold starts the next round.
        @(negedge clk);
        button = 1'b1;
        wait (dut.press === 1'b1);
        second_sampled_delay = dut.core.sampled_delay;
        @(posedge clk);
        #2;
        check(dut.core.state === WAITING, "button in hold starts the next round");
        check(second_sampled_delay >= 1000 && second_sampled_delay <= 10000,
              "next round also gets an in-range random delay");
        dut.core.wait_target = 32'd15;
        @(negedge clk);
        button = 1'b0;
        wait (dut.inputs.armed === 1'b1);
        #2;
        check(wait_entries == 2, "second round entered wait state");

        while (dut.core.state !== REACTING)
            tick;
        check(led[0] === 1'b1, "restarted round also turns LED on");

        // Direct BCD converter checks.
        converter_input = 17'd0; #1;
        check(converter_output === 20'h00000, "BCD converts zero");
        converter_input = 17'd9; #1;
        check(converter_output === 20'h00009, "BCD converts one digit");
        converter_input = 17'd10; #1;
        check(converter_output === 20'h00010, "BCD crosses units boundary");
        converter_input = 17'd99999; #1;
        check(converter_output === 20'h99999, "BCD converts display maximum");

        $display("LAB_PASS reaction_timer_lcd checks=%0d", checks);
        $finish;
    end
endmodule
