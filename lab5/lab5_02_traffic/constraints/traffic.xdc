# Combo II-DLD S75 / MAIN CLOCK F = 50 MHz.
# 핀 출처: 장비 교재 3.5절 [실습 37] 신호등 제어하기의 핀 표(p.657~658).
#   신호등 모듈은 확장포트 EXT41~64에 꽂혀 있다(교재 p.70~71의 EXT 표와 대조함).
#   인덱스 3·2·1·0 = 남(S)·북(N)·서(W)·동(E). 보행자 신호는 S_W·N_W·W_W·E_W.
# flicker는 교재의 flicker 포트와 같은 버튼 SW2(N8)다. 이 설계의 flicker는 HIGH인 동안만
#   점멸 모드이므로 버튼을 누르고 있는 동안 점멸한다(교재의 sw_flicker 토글은 쓰지 않음).
set_property PACKAGE_PIN B6 [get_ports clk_50mhz]
set_property PACKAGE_PIN K4 [get_ports rst_p]
set_property PACKAGE_PIN N8 [get_ports flicker]

set_property PACKAGE_PIN E16 [get_ports {led_green[3]}]
set_property PACKAGE_PIN C16 [get_ports {led_green[2]}]
set_property PACKAGE_PIN A20 [get_ports {led_green[1]}]
set_property PACKAGE_PIN E11 [get_ports {led_green[0]}]
set_property PACKAGE_PIN L18 [get_ports {led_yellow[3]}]
set_property PACKAGE_PIN A14 [get_ports {led_yellow[2]}]
set_property PACKAGE_PIN C18 [get_ports {led_yellow[1]}]
set_property PACKAGE_PIN D13 [get_ports {led_yellow[0]}]
set_property PACKAGE_PIN F15 [get_ports {led_left[3]}]
set_property PACKAGE_PIN D15 [get_ports {led_left[2]}]
set_property PACKAGE_PIN C19 [get_ports {led_left[1]}]
set_property PACKAGE_PIN F10 [get_ports {led_left[0]}]
set_property PACKAGE_PIN B13 [get_ports {led_red[3]}]
set_property PACKAGE_PIN G14 [get_ports {led_red[2]}]
set_property PACKAGE_PIN C17 [get_ports {led_red[1]}]
set_property PACKAGE_PIN C12 [get_ports {led_red[0]}]
set_property PACKAGE_PIN E19 [get_ports {led_walk_green[3]}]
set_property PACKAGE_PIN F12 [get_ports {led_walk_green[2]}]
set_property PACKAGE_PIN A16 [get_ports {led_walk_green[1]}]
set_property PACKAGE_PIN G11 [get_ports {led_walk_green[0]}]
set_property PACKAGE_PIN A19 [get_ports {led_walk_red[3]}]
set_property PACKAGE_PIN G13 [get_ports {led_walk_red[2]}]
set_property PACKAGE_PIN E18 [get_ports {led_walk_red[1]}]
set_property PACKAGE_PIN C11 [get_ports {led_walk_red[0]}]

set_property IOSTANDARD LVCMOS33 [get_ports *]
create_clock -name clk_50mhz -period 20.000 [get_ports clk_50mhz]
set_false_path -from [get_ports {rst_p flicker}]
