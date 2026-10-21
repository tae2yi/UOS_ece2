#!/usr/bin/env bash
# STM32_2 호스트 시뮬레이션 실행. PC용 C 컴파일러를 쓴다.
# Windows에서는 Vivado에 들어 있는 MinGW gcc, macOS·Linux에서는 PATH의 cc(clang/gcc)를 쓴다.
# 사용: bash run_hostsim.sh   (결과는 results/)  다른 컴파일러: CC=clang bash run_hostsim.sh
# results/<이름>_vcp.txt  : MCU가 PC(Serial Monitor)로 출력한 글
# results/<이름>_uart3.hex: MCU가 UART3로 FPGA에 보낸 바이트. lab6_04_uart_led의 TB가 읽는다.
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

"$CC" $CFLAGS $INC -DSTM32_2_TASK=5 hostsim.c "$ROUTINE" -o build/task5.exe
"$CC" $CFLAGS $INC -DSTM32_2_TASK=6 hostsim.c "$ROUTINE" -o build/task6.exe

run() { # 실행 파일, 결과 이름, PC가 보낼 바이트(printf 형식)
    printf "$3" > "results/$2_pc.bin"
    local hex=""; [ "$1" = task6 ] && hex="results/$2_uart3.hex"
    ./build/"$1".exe $hex < "results/$2_pc.bin" > "results/$2_vcp.txt"
    echo "== $2 ($1, PC 입력 $(wc -c < "results/$2_pc.bin") B)"
    cat "results/$2_vcp.txt"
}
# 과제5: 매뉴얼의 세 문자, 줄바꿈 CR LF를 켠 경우, 한글 한 글자(UTF-8 3바이트)
run task5 task5_chars '1Aa'
run task5 task5_crlf 'A\r\n'
run task5 task5_utf8 '\xea\xb0\x80'
# 과제6: 같은 세 문자를 FPGA로 전달
run task6 task6_chars '1Aa'
# 과제7: LED 명령. 1 반복, 2 반복, 0, 그 밖의 문자, 다시 2
run task6 task7_cmds '1122200x2'
