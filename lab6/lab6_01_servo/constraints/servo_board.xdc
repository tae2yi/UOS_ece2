# Combo II-DLD S75 / MAIN CLOCK F = 50 MHz.
# 버튼 핀은 LAB5 피아노와 같은 조교 키패드 예제의 keys 표(N8 = SW2, N4 = SW3).
# servo 출력 핀: 장비 교재 서보모터 실습 핀 구성표 SERVO = AA22.
set_property PACKAGE_PIN B6 [get_ports clk_50mhz]
set_property PACKAGE_PIN K4 [get_ports rst_p]
set_property PACKAGE_PIN N8 [get_ports button_left]
set_property PACKAGE_PIN N4 [get_ports button_right]
set_property PACKAGE_PIN AA22 [get_ports servo]
set_property IOSTANDARD LVCMOS33 [get_ports *]
create_clock -name clk_50mhz -period 20.000 [get_ports clk_50mhz]
set_false_path -from [get_ports {rst_p button_left button_right}]
