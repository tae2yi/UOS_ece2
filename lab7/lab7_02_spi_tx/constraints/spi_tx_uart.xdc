# Combo II-DLD S75 / MAIN CLOCK F = 50 MHz / UART 9600 8N1 — STM32_3 과제11·12 송신 측(마스터)
# SPI 출력은 브레드보드 I/O BDIO_0~2(수신 측 lab7_01과 같은 핀). DIP SW5(BD_SEL)를 켜야 연결된다.
#   spi_sck  = BDIO_0 (F8)  -> MCU PB3  / 상대 FPGA BDIO_0
#   spi_mosi = BDIO_1 (E8)  -> MCU PA7  / 상대 FPGA BDIO_1
#   spi_cs_n = BDIO_2 (A7)  -> MCU PA4(SPI1 NSS, 수신 측) / 상대 FPGA BDIO_2
#   GND      = 옆 헤더 J6   -> MCU GND  / 상대 보드 GND
# SCK 500 kHz(50 MHz / 100). 3.3 V 출력, 버스 스위치 100 ohm 직렬.
# uart_txd = F6(보드 USB-UART). led[7] = LED1 ... led[0] = LED8.
set_property PACKAGE_PIN B6 [get_ports clk_50mhz]
set_property PACKAGE_PIN K4 [get_ports rst_p]
set_property PACKAGE_PIN F8 [get_ports spi_sck]
set_property PACKAGE_PIN E8 [get_ports spi_mosi]
set_property PACKAGE_PIN A7 [get_ports spi_cs_n]
set_property PACKAGE_PIN F6 [get_ports uart_txd]
set_property PACKAGE_PIN L4 [get_ports {led[7]}]
set_property PACKAGE_PIN M4 [get_ports {led[6]}]
set_property PACKAGE_PIN M2 [get_ports {led[5]}]
set_property PACKAGE_PIN N7 [get_ports {led[4]}]
set_property PACKAGE_PIN M7 [get_ports {led[3]}]
set_property PACKAGE_PIN M3 [get_ports {led[2]}]
set_property PACKAGE_PIN M1 [get_ports {led[1]}]
set_property PACKAGE_PIN N5 [get_ports {led[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports *]
create_clock -name clk_50mhz -period 20.000 [get_ports clk_50mhz]
set_false_path -from [get_ports rst_p]
set_false_path -to [get_ports {spi_sck spi_mosi spi_cs_n uart_txd led[*]}]
