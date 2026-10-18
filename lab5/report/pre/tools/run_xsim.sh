#!/usr/bin/env bash
# LAB5 FPGA 3개 실습의 tb·tb_view를 Vivado xsim으로 실행하고 로그·WDB·WCFG를 남긴다.
# 사용: run_xsim.sh <작업 폴더>   (Vivado bin 경로는 VIVADO_BIN으로 바꿀 수 있다)
# 결과: <작업 폴더>/<프로젝트>_<tb>/{tb_sim.wdb,<tb>.wcfg}, report/pre/logs/<프로젝트>_<tb>_xsim.txt
set -euo pipefail
WORK=$1
VIVADO_BIN=${VIVADO_BIN:-/c/AMDDesignTools/2025.2/Vivado/bin}
HERE=$(cd "$(dirname "$0")/.." && pwd)
LAB5=$(cd "$HERE/../.." && pwd)
LOGS=$HERE/logs
mkdir -p "$WORK" "$LOGS"

# 프로젝트 tb 신호목록(경로:radix, 공백 구분)
waves() {
    case "$1_$2" in
    lab5_01_piano_tb_view|lab5_01_piano_tb)
        echo "rst:bin key:hex dut/frequency_hz:unsigned dut/u_tone/count:unsigned piezo:bin" ;;
    lab5_02_traffic_tb_view)
        echo "rst:bin flicker:bin dut/tick:bin dut/blink:bin dut/direction:unsigned dut/phase:unsigned red:bin yellow:bin green:bin walk_red:bin walk_green:bin" ;;
    lab5_02_traffic_tb)
        echo "rst:bin flicker:bin dut/tick:bin dut/blink:bin dut/direction:unsigned dut/phase:unsigned red:bin yellow:bin green:bin wr:bin wg:bin" ;;
    lab5_03_adc_tb_view|lab5_03_adc_tb)
        echo "rst:bin channel:unsigned cs_n:bin sclk:bin mosi:bin miso:bin dut/u_serial/rx_word:hex valid:bin sample:hex led:hex" ;;
    esac
}

for proj in lab5_01_piano lab5_02_traffic lab5_03_adc; do
    for tb in tb tb_view; do
        dir=$WORK/${proj}_$tb
        rm -rf "$dir"; mkdir -p "$dir"
        cp "$LAB5/$proj"/src/*.v "$LAB5/$proj/sim/$tb.sv" "$dir/"
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
        grep -E "PASS|FATAL|Error|\\\$finish|Exiting" "$dir/sim.log" | tee "$LOGS/${proj}_${tb}_xsim.txt"
    done
done
