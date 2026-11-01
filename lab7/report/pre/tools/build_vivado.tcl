# LAB7 FPGA 보드 설계 2개(SPI 수신, SPI 송신)의 합성, 배치·배선, bitstream을 비프로젝트 모드로 실행한다.
# 사용: vivado -mode batch -source build_vivado.tcl -tclargs <lab7 폴더>
# lab7_03_spi_link는 두 설계를 잇는 시뮬레이션 전용이라 구현하지 않는다(과제12는 두 보드에 01·02를 각각 올린다).
set lab [file normalize [lindex $argv 0]]
set part xc7s75fgga484-1
set logs $lab/report/pre/logs
file mkdir $logs

proc read_srcs {dir} {
    set json [read [open $dir/simulation.json]]
    regexp {"sources": \[([^\]]*)\]} $json -> list
    foreach f [regexp -all -inline {"[^"]+"} $list] {
        read_verilog $dir/[string trim $f {"}]
    }
}

foreach {proj top xdc} {
    lab7_01_spi_rx spi_rx_uart constraints/spi_rx_uart.xdc
    lab7_02_spi_tx spi_tx_uart constraints/spi_tx_uart.xdc
} {
    set dir $lab/$proj
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
    report_io -file $logs/${proj}_io.rpt
    file mkdir $dir/bitstream
    write_bitstream -force $dir/bitstream/$top.bit
}
