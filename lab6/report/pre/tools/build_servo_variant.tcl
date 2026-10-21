# 서보 대비안(servo_pwm_mul.v)의 배치·배선 타이밍만 확인한다.
set d [lindex $argv 0]
set logs [lindex $argv 1]
create_project -in_memory -part xc7s75fgga484-1
foreach f {servo_position.v servo_ctrl.v button_pulse.v servo_board.v} { read_verilog $d/src/$f }
read_verilog $d/variants/servo_pwm_mul.v
read_xdc $d/constraints/servo_board.xdc
synth_design -top servo_board
opt_design; place_design; route_design
report_utilization -file $logs/lab6_01_servo_variant_utilization.rpt
report_timing_summary -file $logs/lab6_01_servo_variant_timing.rpt
