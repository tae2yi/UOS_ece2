#!/usr/bin/env bash
# STM32_1 호스트 시뮬레이션 실행. PC용 C 컴파일러를 쓴다.
# Windows에서는 Vivado에 들어 있는 MinGW gcc, macOS·Linux에서는 PATH의 cc(clang/gcc)를 쓴다.
# 사용: bash run_hostsim.sh   (결과는 results/*.csv)  다른 컴파일러: CC=clang bash run_hostsim.sh
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

build() { # 이름, 소스, 추가 옵션
    "$CC" $CFLAGS $INC ${3:-} hostsim.c "$2" -o "build/$1.exe"
}
build task3 "$ROUTINE" -DSTM32_1_TASK=3
build task4 "$ROUTINE" -DSTM32_1_TASK=4
build guard3 variants/release_guard.c -DSTM32_1_TASK=3
build guard4 variants/release_guard.c -DSTM32_1_TASK=4

run() { ./build/"$1".exe "$2" > "results/$1_$2.csv"; echo "results/$1_$2.csv $(wc -l < "results/$1_$2.csv") lines"; }
for s in cycle hold bounce lock; do run task3 "$s"; done
run task4 pwm
run task4 pwm_bounce
for s in cycle hold bounce; do run guard3 "$s"; done
run guard4 pwm
run guard4 pwm_bounce
