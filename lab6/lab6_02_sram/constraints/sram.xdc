# Combo II-DLD S75 / SRAM 4 Mbit(256K x 16).
# 입력 스위치: address[3:0] = DIP_SW1~4, data_in[3:0] = DIP_SW5~8 (LAB2 XDC의 DIP 핀 순서).
# ctrl_w = SW2(N8), ctrl_r = SW3(N4) 버튼. led_out[7:0] = LED1~8.
# SRAM의 ram_cs·ram_oe·ram_we·ram_address[17:0]·ram_data[15:0] 핀은 아직 확인하지 못했다.
# 장비 교재 SRAM 실습의 핀 표를 보고 채운 뒤 bitstream을 만든다. 그 전에는 합성·배치배선까지만 실행한다.
set_property PACKAGE_PIN Y1 [get_ports {address[3]}]
set_property PACKAGE_PIN W3 [get_ports {address[2]}]
set_property PACKAGE_PIN U2 [get_ports {address[1]}]
set_property PACKAGE_PIN T1 [get_ports {address[0]}]
set_property PACKAGE_PIN W4 [get_ports {data_in[3]}]
set_property PACKAGE_PIN W1 [get_ports {data_in[2]}]
set_property PACKAGE_PIN V4 [get_ports {data_in[1]}]
set_property PACKAGE_PIN U4 [get_ports {data_in[0]}]
set_property PACKAGE_PIN N8 [get_ports ctrl_w]
set_property PACKAGE_PIN N4 [get_ports ctrl_r]
set_property PACKAGE_PIN L4 [get_ports {led_out[7]}]
set_property PACKAGE_PIN M4 [get_ports {led_out[6]}]
set_property PACKAGE_PIN M2 [get_ports {led_out[5]}]
set_property PACKAGE_PIN N7 [get_ports {led_out[4]}]
set_property PACKAGE_PIN M7 [get_ports {led_out[3]}]
set_property PACKAGE_PIN M3 [get_ports {led_out[2]}]
set_property PACKAGE_PIN M1 [get_ports {led_out[1]}]
set_property PACKAGE_PIN N5 [get_ports {led_out[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports *]
