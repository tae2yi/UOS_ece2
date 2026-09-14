module seg_decoder(input wire [3:0] bcd, output reg [7:0] seg_data);
  // [7:0] = {a,b,c,d,e,f,g,dp}; active high; hexadecimal 0..F; dp off.
  always @* begin
    case (bcd)
      0:seg_data=8'hfc; 1:seg_data=8'h60; 2:seg_data=8'hda; 3:seg_data=8'hf2;
      4:seg_data=8'h66; 5:seg_data=8'hb6; 6:seg_data=8'hbe; 7:seg_data=8'he0;
      8:seg_data=8'hfe; 9:seg_data=8'hf6; 10:seg_data=8'hee; 11:seg_data=8'h3e;
      12:seg_data=8'h9c; 13:seg_data=8'h7a; 14:seg_data=8'h9e; 15:seg_data=8'h8e;
      default:seg_data=0;
    endcase
  end
endmodule
