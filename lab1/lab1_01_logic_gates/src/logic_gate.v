// PDF의 회로 코드를 여기에 직접 작성하고 저장하세요.
// 파일명을 바꾸거나 하위 모듈을 추가하면 simulation.json의 sources도 수정하세요.
module logic_gate(input wire a,b, output wire x,y,z);
    assign x = a & b;
    assign y = a | b;
    assign z = a ^ b;
endmodule