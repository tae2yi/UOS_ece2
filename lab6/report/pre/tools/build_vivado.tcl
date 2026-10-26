# LAB6 FPGA 4개 설계의 합성, 배치·배선, bitstream까지 비프로젝트 모드로 실행한다.
# 사용: vivado -mode batch -source build_vivado.tcl -tclargs <lab6 폴더>
# 서보는 장치 핀이 아직 정해지지 않아 배치·배선과 리포트까지만 하고 bitstream은 만들지 않는다.
set lab6 [file normalize [lindex $argv 0]]
set part xc7s75fgga484-1
set logs $lab6/report/pre/logs
file mkdir $logs

proc read_srcs {dir} {
    set json [read [open $dir/simulation.json]]
    regexp {"sources": \[([^\]]*)\]} $json -> list
    foreach f [regexp -all -inline {"[^"]+"} $list] {
        read_verilog $dir/[string trim $f {"}]
    }
}

foreach {proj top xdc bit} {
    lab6_01_servo    servo_board  constraints/servo_board.xdc  0
    lab6_02_sram     sram         constraints/sram.xdc         1
    lab6_03_dac      dac          constraints/dac.xdc          1
    lab6_04_uart_led mcu_uart_led constraints/mcu_uart_led.xdc 1
} {
    set dir $lab6/$proj
    close_project -quiet
    create_project -in_memory -part $part
    read_srcs $dir
    read_xdc $dir/$xdc
    synth_design -top $top -part $part
    report_utilization -file $logs/${proj}_utilization_synth.rpt
    opt_design
    place_design
    route_design
    report_utilization -file $logs/${proj}_utilization.rpt
    report_timing_summary -file $logs/${proj}_timing.rpt
    report_drc -file $logs/${proj}_drc.rpt
    if {$bit} {
        file mkdir $dir/bitstream
        write_bitstream -force $dir/bitstream/$top.bit
    }
}
