#!/usr/bin/env bash
# LAB7 전체 검증: MCU 호스트 시뮬레이션 → FPGA 3개 프로젝트의 tb·tb_view(Icarus) → MCU 슬레이브 호스트 시뮬레이션.
#   1) stm32_3_hostsim: 마스터 MCU가 보낸 바이트(results/master_spi.hex)를 lab7_01_spi_rx/sim/mcu_spi.hex로 복사(과제10 입력)
#   2) lab7_03_spi_link/src는 lab7_01·02의 RTL 사본이다. 실행 전에 다시 복사해 두 프로젝트와 같게 맞춘다.
#   3) lab7_02_spi_tx TB가 MOSI에서 읽은 바이트(sim/fpga_tx_bytes.hex)를 MCU 슬레이브가 받는다(과제11).
# 로그: report/pre/logs/<프로젝트>_<tb>_icarus.txt, stm32_3_hostsim/results/run.log
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
LAB=$(cd "$HERE/../.." && pwd)
export PATH="${IVERILOG_BIN:-/c/iverilog/bin}:$PATH"
LOGS=$HERE/logs; mkdir -p "$LOGS"

bash "$LAB/stm32_3_hostsim/run_hostsim.sh" > /dev/null
cp "$LAB/stm32_3_hostsim/results/master_spi.hex" "$LAB/lab7_01_spi_rx/sim/mcu_spi.hex"
cp "$LAB"/lab7_01_spi_rx/src/*.v "$LAB/lab7_03_spi_link/src/"
cp "$LAB/lab7_02_spi_tx/src/spi_master_tx.v" "$LAB/lab7_02_spi_tx/src/spi_tx_uart.v" "$LAB/lab7_03_spi_link/src/"

for proj in lab7_01_spi_rx lab7_02_spi_tx lab7_03_spi_link; do
    for tb in tb tb_view; do
        (
            cd "$LAB/$proj"; mkdir -p build
            iverilog -g2012 -o build/$tb.vvp src/*.v sim/$tb.sv
            vvp -n build/$tb.vvp | sed "s|$LAB/$proj/||"
        ) | tee "$LOGS/${proj}_${tb}_icarus.txt" | grep -E "PASS|FATAL|FAIL|Error"
    done
done

# 과제11: FPGA 송신 TB 결과를 MCU 슬레이브가 받는다(run_hostsim.sh가 fpga_tx_bytes.hex를 찾아 실행)
bash "$LAB/stm32_3_hostsim/run_hostsim.sh" > /dev/null
echo "== MCU slave <- FPGA (stm32_3_hostsim/results/slave_from_fpga_vcp.txt)"
cat "$LAB/stm32_3_hostsim/results/slave_from_fpga_vcp.txt"
