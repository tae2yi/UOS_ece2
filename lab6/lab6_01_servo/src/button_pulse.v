`timescale 1ns/1ps
// 버튼 원시 신호를 동기화하고, STABLE_CYCLES 동안 같은 값이 유지될 때만 새 값으로 인정합니다.
// 인정된 값이 0 -> 1로 바뀌는 클록에 pulse를 한 클록 동안 1로 냅니다(한 번 누름 = 한 펄스).
// 기본값 1_000_000은 50 MHz에서 20 ms입니다. 접점 떨림은 보통 수 ms 안에 끝납니다.
module button_pulse #(parameter STABLE_CYCLES=1_000_000)(
    input wire clk_50mhz,rst_p,button,
    output reg pulse
);
    (* ASYNC_REG="TRUE" *) reg [1:0] sync;
    reg stable;
    reg [31:0] count;
    always @(posedge clk_50mhz) begin
        if(rst_p) begin sync<=0; stable<=0; count<=0; pulse<=0; end
        else begin
            sync<={sync[0],button};
            pulse<=0;
            if(sync[1]==stable) count<=0;
            else if(count==STABLE_CYCLES-1) begin
                count<=0;
                stable<=sync[1];
                pulse<=sync[1];
            end
            else count<=count+1;
        end
    end
endmodule
