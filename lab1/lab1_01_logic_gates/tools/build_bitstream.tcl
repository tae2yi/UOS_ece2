set part xc7s75fgga484-1
set proj_root [file normalize [file join [file dirname [info script]] ..]]
create_project -force lab1_01_logic_gates $proj_root/vivado -part $part
add_files -norecurse $proj_root/src/logic_gate.v
add_files -fileset constrs_1 -norecurse $proj_root/constraints/logic_gate.xdc
set_property top logic_gate [current_fileset]
update_compile_order -fileset sources_1
launch_runs synth_1 -jobs 4
wait_on_run synth_1
if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {
    error "synth_1 실패: [get_property STATUS [get_runs synth_1]]"
}
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {
    error "impl_1 실패: [get_property STATUS [get_runs impl_1]]"
}
puts "BITSTREAM_DONE: $proj_root/vivado/lab1_01_logic_gates.runs/impl_1/logic_gate.bit"
