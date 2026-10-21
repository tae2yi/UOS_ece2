#!/usr/bin/env bash
# LAB6 FPGA 4개 설계의 tb·tb_view를 Icarus Verilog로 실행하고 로그를 report/pre/logs에 남긴다.
# 과제6·7 TB는 MCU 호스트 시뮬레이션 결과(stm32_2_hostsim/results/*_uart3.hex)를 sim/에 복사해 쓴다.
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
LAB6=$(cd "$HERE/../.." && pwd)
export PATH="${IVERILOG_BIN:-/c/iverilog/bin}:$PATH"
LOGS=$HERE/logs; mkdir -p "$LOGS"
cp "$LAB6/stm32_2_hostsim/results/task6_chars_uart3.hex" "$LAB6/lab6_04_uart_led/sim/mcu_task6.hex"
cp "$LAB6/stm32_2_hostsim/results/task7_cmds_uart3.hex" "$LAB6/lab6_04_uart_led/sim/mcu_task7.hex"
for proj in lab6_01_servo lab6_02_sram lab6_03_dac lab6_04_uart_led; do
    for tb in tb tb_view; do
        (
            cd "$LAB6/$proj"; mkdir -p build
            iverilog -g2012 -o build/$tb.vvp src/*.v sim/$tb.sv
            vvp -n build/$tb.vvp | sed "s|$LAB6/$proj/||"
        ) | tee "$LOGS/${proj}_${tb}_icarus.txt" | grep -E "PASS|FATAL|Error"
    done
done
