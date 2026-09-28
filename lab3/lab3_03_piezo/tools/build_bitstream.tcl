set part xc7s75fgga484-1
set proj_name lab3_03_piezo
set top lab3_piezo
set proj_root [file normalize [file join [file dirname [info script]] ..]]
set evidence_dir $proj_root/evidence/vivado
file mkdir $evidence_dir

create_project -force $proj_name $proj_root/vivado -part $part
add_files -norecurse [list \
    $proj_root/src/lab3_piezo.v]
add_files -fileset sim_1 -norecurse $proj_root/sim/tb_piezo.sv
add_files -fileset constrs_1 -norecurse $proj_root/constraints/lab3_piezo.xdc
set_property top $top [get_filesets sources_1]
set_property top tb_piezo [get_filesets sim_1]
update_compile_order -fileset sources_1

launch_runs synth_1 -jobs 4
wait_on_run synth_1
if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {
    error "synth_1 failed: [get_property STATUS [get_runs synth_1]]"
}
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {
    error "impl_1 failed: [get_property STATUS [get_runs impl_1]]"
}

open_run impl_1
report_drc -file $evidence_dir/drc.rpt
report_timing_summary -file $evidence_dir/timing_summary.rpt
report_clocks -file $evidence_dir/clocks.rpt
report_utilization -file $evidence_dir/utilization.rpt
report_io -file $evidence_dir/io.rpt
puts "WNS: [get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup]]"
# Copy the bit out of the ignored vivado/ folder so it can be committed.
file mkdir $proj_root/bitstream
file copy -force $proj_root/vivado/$proj_name.runs/impl_1/$top.bit $proj_root/bitstream/$top.bit
puts "BITSTREAM_DONE: $proj_root/vivado/$proj_name.runs/impl_1/$top.bit"
