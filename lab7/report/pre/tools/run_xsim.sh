#!/usr/bin/env bash
# LAB7 FPGA 3개 프로젝트의 tb·tb_view를 Vivado xsim으로 실행하고 로그·WDB·WCFG를 남긴다.
# 사용: run_xsim.sh <작업 폴더>   (Vivado bin 경로는 VIVADO_BIN으로 바꿀 수 있다)
# 결과: <작업 폴더>/<프로젝트>_<tb>/{tb_sim.wdb,<tb>.wcfg}, report/pre/logs/<프로젝트>_<tb>_xsim.txt
# 먼저 run_icarus.sh를 실행해 sim/mcu_spi.hex와 lab7_03 소스 사본을 맞춰 둔다.
set -euo pipefail
WORK=$1
VIVADO_BIN=${VIVADO_BIN:-/c/AMDDesignTools/2025.2/Vivado/bin}
HERE=$(cd "$(dirname "$0")/.." && pwd)
LAB=$(cd "$HERE/../.." && pwd)
LOGS=$HERE/logs
mkdir -p "$WORK" "$LOGS"

# 프로젝트 tb 신호목록(경로:radix, 공백 구분)
waves() {
    case "$1_$2" in
    lab7_01_spi_rx_tb)
        echo "rst:bin cs_n:bin sck:bin mosi:bin dut/rx_valid:bin dut/rx_data:hex led:hex dut/u_line/busy:bin txd:bin n_lines:unsigned" ;;
    lab7_01_spi_rx_tb_view)
        echo "cs_n:bin sck:bin mosi:bin dut/u_spi/cs_n_s:bin dut/u_spi/sck_s:bin dut/sck_rise:bin dut/bit_count:unsigned dut/u_spi/shift:bin dut/rx_valid:bin dut/rx_data:hex txd:bin" ;;
    lab7_02_spi_tx_tb)
        echo "rst:bin dut/start:bin dut/value:hex cs_n:bin sck:bin mosi:bin dut/done:bin led:hex txd:bin n_bytes:unsigned" ;;
    lab7_02_spi_tx_tb_view)
        echo "dut/start:bin dut/value:hex dut/u_spi/state:unsigned cs_n:bin sck:bin mosi:bin dut/u_spi/bit_index:unsigned dut/u_spi/shift:bin dut/done:bin got:hex" ;;
    lab7_03_spi_link_tb)
        echo "rst:bin board_a/value:hex cs_n_a:bin sck_a:bin mosi_a:bin txd_a:bin board_b/rx_valid:bin board_b/rx_data:hex led_b:hex txd_b:bin" ;;
    lab7_03_spi_link_tb_view)
        echo "clk_a:bin clk_b:bin cs_n_a:bin sck_a:bin mosi_a:bin sck_b:bin board_b/sck_rise:bin board_b/bit_count:unsigned board_b/rx_valid:bin board_b/rx_data:hex led_b:hex" ;;
    esac
}

for proj in lab7_01_spi_rx lab7_02_spi_tx lab7_03_spi_link; do
    for tb in tb tb_view; do
        dir=$WORK/${proj}_$tb
        rm -rf "$dir"; mkdir -p "$dir/sim"
        cp "$LAB/$proj"/src/*.v "$LAB/$proj/sim/$tb.sv" "$dir/"
        if ls "$LAB/$proj"/sim/*.hex >/dev/null 2>&1; then cp "$LAB/$proj"/sim/*.hex "$dir/sim/"; fi
        {
            echo "log_wave -r /"
            for w in $(waves $proj $tb); do
                echo "add_wave -radix ${w#*:} /$tb/${w%%:*}"
            done
            echo "run all"
            echo "save_wave_config $tb.wcfg"
            echo "exit"
        } > "$dir/wave.tcl"
        (
            cd "$dir"
            "$VIVADO_BIN/xvlog.bat" -sv *.v "$tb.sv" > compile.log
            "$VIVADO_BIN/xelab.bat" -debug typical "$tb" -s tb_sim > elab.log
            "$VIVADO_BIN/xsim.bat" tb_sim -tclbatch wave.tcl < /dev/null > sim.log
        )
        grep -E "PASS|FATAL|FAIL|Error|\\\$finish|Exiting" "$dir/sim.log" | tee "$LOGS/${proj}_${tb}_xsim.txt"
        # 긴 tb(약 90 ms)는 GUI가 0~700 ms로 넓게 열어 파형이 왼쪽에 몰린다.
        # 캡처할 때 capture_xsim.ps1 -Keys "^0"(Zoom Fit)을 준다.
    done
done
