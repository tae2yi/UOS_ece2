# Combo II-DLD S75 / MAIN CLOCK F = 50 MHz.
# 버튼 핀은 LAB5 피아노와 같은 조교 키패드 예제의 keys 표(N8 = SW2, N4 = SW3).
# servo 출력 핀은 아직 확인하지 못했다. 장비 교재 서보모터 실습의 핀 표를 보고 아래 줄의 주석을 풀어 채운다.
# 그 전까지는 bitstream을 만들지 않는다(빌드 스크립트는 합성·배치배선까지만 실행).
set_property PACKAGE_PIN B6 [get_ports clk_50mhz]
set_property PACKAGE_PIN K4 [get_ports rst_p]
set_property PACKAGE_PIN N8 [get_ports button_left]
set_property PACKAGE_PIN N4 [get_ports button_right]
# set_property PACKAGE_PIN ?? [get_ports servo]
set_property IOSTANDARD LVCMOS33 [get_ports *]
create_clock -name clk_50mhz -period 20.000 [get_ports clk_50mhz]
set_false_path -from [get_ports {rst_p button_left button_right}]
