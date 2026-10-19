# Combo II-DLD S75 / MAIN CLOCK F = 50 MHz. 설계 top은 adc_board(adc를 감싼 보드용 top).
# 핀 출처: 장비 교재 [실습 36] ADC를 통해 센서 값 읽기의 핀 구성표(p.632).
#   ADC 칩은 AD7908(8채널, 8비트). 교재 기준 ch0 CdS, ch1 가변저항.
#   SPI_AD는 칩 선택(CS)이다.
# add_sel[0]=DIP_SW1(Y1)은 교재 p.625 표. add_sel[2:1]은 LAB1의 벤더 예제에서 Y1과 함께
#   쓰인 스위치 W3·U2를 이어 붙였다(DIP_SW2·3로 추정, 실험 전 확인). ch0/ch1만 쓰면 둘 다 0.
# LED 순서는 교재 p.625 표: led_out[7]=LED1(L4) ... led_out[0]=LED8(N5).
set_property PACKAGE_PIN B6 [get_ports clk_50mhz]
set_property PACKAGE_PIN K4 [get_ports rst_p]
set_property PACKAGE_PIN Y1 [get_ports {add_sel[0]}]
set_property PACKAGE_PIN W3 [get_ports {add_sel[1]}]
set_property PACKAGE_PIN U2 [get_ports {add_sel[2]}]

set_property PACKAGE_PIN H3 [get_ports adc_ncs]
set_property PACKAGE_PIN H5 [get_ports adc_din]
set_property PACKAGE_PIN J6 [get_ports adc_dout]
set_property PACKAGE_PIN H7 [get_ports adc_sclk]

set_property PACKAGE_PIN L4 [get_ports {led_out[7]}]
set_property PACKAGE_PIN M4 [get_ports {led_out[6]}]
set_property PACKAGE_PIN M2 [get_ports {led_out[5]}]
set_property PACKAGE_PIN N7 [get_ports {led_out[4]}]
set_property PACKAGE_PIN M7 [get_ports {led_out[3]}]
set_property PACKAGE_PIN M3 [get_ports {led_out[2]}]
set_property PACKAGE_PIN M1 [get_ports {led_out[1]}]
set_property PACKAGE_PIN N5 [get_ports {led_out[0]}]

set_property IOSTANDARD LVCMOS33 [get_ports *]
create_clock -name clk_50mhz -period 20.000 [get_ports clk_50mhz]
set_false_path -from [get_ports {rst_p add_sel[*] adc_dout}]
set_false_path -to [get_ports {adc_sclk adc_ncs adc_din led_out[*]}]
