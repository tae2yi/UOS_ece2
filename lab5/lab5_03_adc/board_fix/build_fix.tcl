# 수정본 ADC bitstream: board_fix/serial_frame16.v로 바꿔 끼운 adc_board.
# 사용: vivado -mode batch -source board_fix/build_fix.tcl -tclargs <lab5_03_adc 폴더>
set dir [file normalize [lindex $argv 0]]
create_project -in_memory -part xc7s75fgga484-1
read_verilog [list $dir/src/adc_command.v $dir/board_fix/serial_frame16.v $dir/src/adc.v $dir/src/adc_board.v]
read_xdc $dir/constraints/adc_board.xdc
synth_design -top adc_board -part xc7s75fgga484-1
opt_design
place_design
route_design
report_timing_summary -file $dir/board_fix/timing.rpt
report_drc -file $dir/board_fix/drc.rpt
write_bitstream -force $dir/bitstream/adc_board_fix.bit
