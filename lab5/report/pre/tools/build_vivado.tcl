# LAB5 FPGA 3개 설계의 합성과(피아노는) 배치·배선·bitstream까지 비프로젝트 모드로 실행한다.
# 사용: vivado -mode batch -source build_vivado.tcl -tclargs <lab5 폴더> <작업 폴더>
# 신호등·ADC는 교재 핀 표가 없어 XDC 없이 합성만 해 자원 사용량을 본다.
set lab5 [file normalize [lindex $argv 0]]
set work [file normalize [lindex $argv 1]]
set part xc7s75fgga484-1
set logs $lab5/report/pre/logs
file mkdir $logs

proc read_srcs {dir} {
    set json [read [open $dir/simulation.json]]
    regexp {"sources": \[([^\]]*)\]} $json -> list
    foreach f [regexp -all -inline {"[^"]+"} $list] {
        read_verilog $dir/[string trim $f {"}]
    }
}

foreach {proj top xdc} {
    lab5_01_piano   piano   constraints/piano.xdc
    lab5_02_traffic traffic {}
    lab5_03_adc     adc     {}
} {
    set dir $lab5/$proj
    close_project -quiet
    create_project -in_memory -part $part
    read_srcs $dir
    if {$xdc ne ""} { read_xdc $dir/$xdc }
    synth_design -top $top -part $part
    report_utilization -file $logs/${proj}_utilization_synth.rpt
    if {$xdc ne ""} {
        opt_design
        place_design
        route_design
        report_utilization -file $logs/${proj}_utilization.rpt
        report_timing_summary -file $logs/${proj}_timing.rpt
        report_drc -file $logs/${proj}_drc.rpt
        file mkdir $dir/bitstream
        write_bitstream -force $dir/bitstream/$top.bit
    }
}
