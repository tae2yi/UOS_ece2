# Combo II-DLD S75 / MAIN CLOCK F = 50 MHz / UART 9600 8N1.
# LAB3-07 UART 에코의 XDC에서 RX만 바꿨다. 기존 RX C6(보드 USB-UART)은 쓰지 않는다.
# mcu_rxd = 브레드보드 I/O BDIO_0(F8). MCU PC10(UART3 TX)을 점퍼선으로 연결하고 GND는 옆 헤더 J6에 잇는다.
#   BDIO는 DIP SW5(BD_SEL)로 켜야 연결된다(장비 교재 브레드보드 I/O 표). 3.3 V 입력이고 100 Ω 직렬 저항이 있다.
#   선을 뺐을 때 입력이 떠서 잡음 프레임이 들어오지 않도록 내부 풀업을 켠다(UART 대기 상태 = HIGH).
# uart_txd = F6(보드 USB-UART) 그대로. led_cmd = LED1, led_byte[6:0] = LED2~8.
set_property PACKAGE_PIN B6 [get_ports clk_50mhz]
set_property PACKAGE_PIN K4 [get_ports rst_p]
set_property PACKAGE_PIN F8 [get_ports mcu_rxd]
set_property PULLUP true [get_ports mcu_rxd]
set_property PACKAGE_PIN F6 [get_ports uart_txd]
set_property PACKAGE_PIN L4 [get_ports led_cmd]
set_property PACKAGE_PIN M4 [get_ports {led_byte[6]}]
set_property PACKAGE_PIN M2 [get_ports {led_byte[5]}]
set_property PACKAGE_PIN N7 [get_ports {led_byte[4]}]
set_property PACKAGE_PIN M7 [get_ports {led_byte[3]}]
set_property PACKAGE_PIN M3 [get_ports {led_byte[2]}]
set_property PACKAGE_PIN M1 [get_ports {led_byte[1]}]
set_property PACKAGE_PIN N5 [get_ports {led_byte[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports *]
create_clock -name clk_50mhz -period 20.000 [get_ports clk_50mhz]
set_false_path -from [get_ports {rst_p mcu_rxd}]
