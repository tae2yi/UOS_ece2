#!/usr/bin/env bash
# LAB6 FPGA 4개 실습의 tb·tb_view를 Vivado xsim으로 실행하고 로그·WDB·WCFG를 남긴다.
# 사용: run_xsim.sh <작업 폴더>   (Vivado bin 경로는 VIVADO_BIN으로 바꿀 수 있다)
# 결과: <작업 폴더>/<프로젝트>_<tb>/{tb_sim.wdb,<tb>.wcfg}, report/pre/logs/<프로젝트>_<tb>_xsim.txt
set -euo pipefail
WORK=$1
VIVADO_BIN=${VIVADO_BIN:-/c/AMDDesignTools/2025.2/Vivado/bin}
HERE=$(cd "$(dirname "$0")/.." && pwd)
LAB6=$(cd "$HERE/../.." && pwd)
LOGS=$HERE/logs
mkdir -p "$WORK" "$LOGS"

# 프로젝트 tb 신호목록(경로:radix, 공백 구분)
waves() {
    case "$1_$2" in
    lab6_01_servo_tb)
        echo "rst:bin l:bin r:bin us:unsigned pwm_dut/width_cycles:unsigned pwm_dut/count:unsigned servo:bin" ;;
    lab6_01_servo_tb_view)
        echo "rst:bin left:bin right:bin dut/left_pulse:bin dut/right_pulse:bin dut/u_servo/pulse_us:unsigned dut/u_servo/u_pwm/width_cycles:unsigned dut/u_servo/u_pwm/count:unsigned servo:bin" ;;
    lab6_02_sram_tb|lab6_02_sram_tb_view)
        echo "wr:bin rd:bin address:hex data_in:hex cs_n:bin oe_n:bin we_n:bin bus:hex led:hex" ;;
    lab6_03_dac_tb|lab6_03_dac_tb_view)
        echo "rst:bin channel:bin dut/update:bin we_n:bin a_b:bin data:unsigned led:hex" ;;
    lab6_04_uart_led_tb|lab6_04_uart_led_tb_view)
        echo "rst:bin rxd:bin dut/rx_valid:bin dut/rx_data:hex led_cmd:bin led_byte:hex dut/tx_valid:bin txd:bin" ;;
    esac
}

for proj in lab6_01_servo lab6_02_sram lab6_03_dac lab6_04_uart_led; do
    for tb in tb tb_view; do
        dir=$WORK/${proj}_$tb
        rm -rf "$dir"; mkdir -p "$dir"
        cp "$LAB6/$proj"/src/*.v "$LAB6/$proj/sim/$tb.sv" "$dir/"
        # 과제6·7 TB는 sim/mcu_task*.hex를 읽는다(run_icarus.sh가 호스트 시뮬레이션 결과를 복사해 둔다).
        if ls "$LAB6/$proj"/sim/*.hex >/dev/null 2>&1; then mkdir -p "$dir/sim"; cp "$LAB6/$proj"/sim/*.hex "$dir/sim/"; fi
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
