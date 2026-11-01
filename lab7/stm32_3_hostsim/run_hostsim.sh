#!/usr/bin/env bash
# STM32_3 호스트 시뮬레이션 실행. PC용 C 컴파일러를 쓴다.
# Windows에서는 Vivado에 들어 있는 MinGW gcc, macOS·Linux에서는 PATH의 cc(clang/gcc)를 쓴다.
# 사용: bash run_hostsim.sh   (결과는 results/)  다른 컴파일러: CC=clang bash run_hostsim.sh
# results/master_*        : 마스터(과제8·9·10) VCP 출력, 보낸 바이트(.hex → lab7_01 FPGA 수신 TB 입력), SCK·MOSI·CS 시각표(.csv)
# results/slave_*_vcp.txt : 슬레이브(과제9·11)가 VCP로 출력한 글
#   slave_from_mcu  = 마스터 MCU의 송신 바이트를 그대로 받음(과제9 MCU → MCU)
#   slave_from_fpga = lab7_02 FPGA 송신 TB가 MOSI에서 읽은 바이트를 받음(과제11 FPGA → MCU)
#   slave_timeout   = 중간에 2초 동안 송신이 없는 경우("--")
set -euo pipefail
cd "$(dirname "$0")"
GCC_DIR="${GCC_DIR:-/c/AMDDesignTools/2025.2/Vivado/tps/mingw/10.0.0/win64.o/nt/bin}"
if [ -d "$GCC_DIR" ]; then export PATH="$GCC_DIR:$PATH"; CC="${CC:-gcc}"; fi
CC="${CC:-cc}"
INC="-I mock -I ../stm32_lab/Core/Inc"
CFLAGS="-std=c11 -O1 -Wall -Wextra -Wno-unused-function"
ROUTINE=../stm32_lab/Core/Src/ece2_474_routine.c
mkdir -p build results
exec > >(tee results/run.log) 2>&1

"$CC" $CFLAGS $INC -DSTM32_3_ROLE=1 hostsim.c "$ROUTINE" -o build/master.exe
"$CC" $CFLAGS $INC -DSTM32_3_ROLE=1 -DSTM32_3_TX_FIXED=0x55 hostsim.c "$ROUTINE" -o build/fixed55.exe
"$CC" $CFLAGS $INC -DSTM32_3_ROLE=2 hostsim.c "$ROUTINE" -o build/slave.exe

echo "== master: 8.5 s, 기본(0x55 -> 0xA5 -> 0x00 -> 0xFF 반복)"
./build/master.exe master 8 results/master_spi.hex results/master_wave.csv > results/master_vcp.txt
cat results/master_vcp.txt
echo "== fixed55: 3 s, -DSTM32_3_TX_FIXED=0x55"
./build/fixed55.exe master 3 results/fixed55_spi.hex results/fixed55_wave.csv > results/fixed55_vcp.txt
cat results/fixed55_vcp.txt

slave() { # 결과 이름, 입력 hex
    ./build/slave.exe slave "$2" > "results/$1_vcp.txt"
    echo "== $1 (입력 $2)"
    cat "results/$1_vcp.txt"
}
slave slave_from_mcu results/master_spi.hex
printf '55\n--\na5\n' > results/slave_timeout_in.hex
slave slave_timeout results/slave_timeout_in.hex
if [ -f ../lab7_02_spi_tx/sim/fpga_tx_bytes.hex ]; then
    cp ../lab7_02_spi_tx/sim/fpga_tx_bytes.hex results/fpga_tx_bytes.hex
    slave slave_from_fpga results/fpga_tx_bytes.hex
else
    echo "== slave_from_fpga: lab7_02_spi_tx/sim/fpga_tx_bytes.hex 없음(FPGA TB를 먼저 실행)"
fi
