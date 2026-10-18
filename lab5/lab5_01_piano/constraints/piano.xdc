# Combo II-DLD S75 / MAIN CLOCK F = 50 MHz.
# 버튼 핀: 조교 예제 Glaysia/ece2_26_2_2 example/uart_keypad_test의 keys[0..11] 표
#   (Combo II-DLD 설명서 버튼 핀 표). keys[0]=K4는 LAB3의 rst_p와 같은 버튼이라 리셋으로 쓰고,
#   keys[1..8]을 key[7]=도 ... key[0]=높은 도 순서로 놓았다. piezo는 LAB3-03과 같은 Y21.
# 실험 전 교재 piano.zip의 핀 표와 대조한다.
set_property PACKAGE_PIN B6 [get_ports clk_50mhz]
set_property PACKAGE_PIN K4 [get_ports rst_p]
set_property PACKAGE_PIN N8 [get_ports {key[7]}]
set_property PACKAGE_PIN N4 [get_ports {key[6]}]
set_property PACKAGE_PIN N1 [get_ports {key[5]}]
set_property PACKAGE_PIN P6 [get_ports {key[4]}]
set_property PACKAGE_PIN N6 [get_ports {key[3]}]
set_property PACKAGE_PIN L5 [get_ports {key[2]}]
set_property PACKAGE_PIN J2 [get_ports {key[1]}]
set_property PACKAGE_PIN K2 [get_ports {key[0]}]
set_property PACKAGE_PIN Y21 [get_ports piezo]
set_property IOSTANDARD LVCMOS33 [get_ports *]
create_clock -name clk_50mhz -period 20.000 [get_ports clk_50mhz]
set_false_path -from [get_ports {rst_p key[*]}]
