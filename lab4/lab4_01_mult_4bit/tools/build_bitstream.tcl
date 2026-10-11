set part xc7s75fgga484-1
set proj_name lab4_01_mult_4bit
set top mult_4bit
set proj_root [file normalize [file join [file dirname [info script]] ..]]
set evidence_dir $proj_root/evidence/vivado
file mkdir $evidence_dir

create_project -force $proj_name $proj_root/vivado -part $part
add_files -norecurse [list $proj_root/src/multiply_unsigned.v $proj_root/src/mult_4bit.v]
add_files -fileset sim_1 -norecurse [list $proj_root/sim/tb.sv $proj_root/sim/tb_view.sv]
add_files -fileset constrs_1 -norecurse $proj_root/constraints/mult_4bit.xdc
set_property top $top [get_filesets sources_1]
set_property top tb [get_filesets sim_1]
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
report_utilization -file $evidence_dir/utilization.rpt
report_io -file $evidence_dir/io.rpt
# 조합회로라 클록이 없다. 보고용으로만 입력->출력 경로에 max delay를 걸어 가장 긴 경로 지연을 읽는다.
set_max_delay 100.000 -from [all_inputs] -to [all_outputs]
report_timing -from [all_inputs] -to [all_outputs] -max_paths 1 -file $evidence_dir/longest_path.rpt
set p [get_timing_paths -from [all_inputs] -to [all_outputs] -max_paths 1 -nworst 1]
puts "LONGEST_PATH_NS: [get_property DATAPATH_DELAY $p] ([get_property STARTPOINT_PIN $p] -> [get_property ENDPOINT_PIN $p])"
# Copy the bit out of the ignored vivado/ folder so it can be committed.
file mkdir $proj_root/bitstream
file copy -force $proj_root/vivado/$proj_name.runs/impl_1/$top.bit $proj_root/bitstream/$top.bit
puts "BITSTREAM_DONE: $proj_root/vivado/$proj_name.runs/impl_1/$top.bit"
