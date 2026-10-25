# LAB1~LAB3 (FPGA 기초, 9/14~9/28) — 완료

모두 fpga-lab-template v2.0.2로 실험별 폴더를 만들고(.git 삭제), Icarus + Vivado 시뮬레이션, 합성·구현·bitstream.

## LAB1 조합회로 10개 (9/14)

`lab1_01_logic_gates, 02_full_adder, 03_adder4, 04_subtractor4, 05_comparator4, 06_mux4to1, 07_demux1to8, 08_encoder8to3, 09_decoder3to8, 10_seven_segment`
- 보고서: `lab1/report/pre/LAB1_예비보고서.docx`, `lab1/report/results/LAB1_결과보고서_수정본_v3.docx`(+`_최종.pdf`). 실험별 `reports/pre/README.md`.
- 영상: YouTube 재생목록(루트 README). LAB1 XDC가 DIP 스위치 핀의 근거(a[3]=Y1, 디멀티플렉서 s[2:0]=Y1·W3·U2).

## LAB2 순차회로 8개 (9/21)

`lab2_01_counter, 02_clock_divider, 03_register, 04_shift_register, 05_piso, 06_moore, 07_mealy, 08_segment_scan`
- 실험마다 `MODIFICATION_EXPERIMENT.md`, `CHANGELOG.md`, `evidence/{normal,modified,recovered}`. `lab2/AGENTS.md`: 수정 실험은 정상 실험 VCD 캡처 후에만.
- 보고서: `lab2/reports/pre/LAB2_실험전보고서_레이아웃수정본.docx`(+build_lab2_report.py), `lab2/reports/final/LAB2_결과보고서.docx`(+build_lab2_final.py, make_figures.py).
- 결과보고서 작업 중 사용자 지시: 통합본(+6.3) 내용 제외, 00 PDF와 대조해 빠진 항목 보강, 파형 비교에 해석, 보드 사진 부분은 해당 실험의 파형·해석과 비교. Lab 2.01 수정 실험 추가.
- 영상: YouTube 재생목록 <https://youtube.com/playlist?list=PLbHlLnDMwa6Y&si=6yP5VxLgyYnV-kgB>.

## LAB3 주변장치 7개 (9/28)

`lab3_01_led_pwm, 02_rgb_pwm, 03_piezo, 04_stepper, 05_mmss_clock, 06_character_lcd, 07_uart_echo`
(TB top: tb_led_pwm, tb_rgb_pwm, tb_piezo, tb_stepper, tb_mmss_counter, tb_character_lcd, tb_uart_echo)
- 교안 PDF는 교육 번호 19~25지만 폴더는 01~07(사용자 지시).
- 수정 실험 7건은 정상 실험 후 `report/pre/mod/`에서 진행(정상 bitstream·프로젝트 보존).
- bitstream을 `bitstream/`에 커밋(+`BUILD_INFO.txt`) — 교안(START)의 "build·Vivado 파일 커밋 금지"와 어긋날 수 있으나 사용자가 원했고, **보고서에 그 사실을 적지 말라고 함.**
- 예비보고서 `lab3/report/pre/LAB3_예비보고서.docx`(코드마다 GitHub 주소). 결과보고서 `lab3/report/final/LAB3_결과보고서.docx`, 태그 `lab3-final`.
- 실습 시연은 **07 UART 에코**. 영상 7개 `lab3/report/final/video/`(README에 시연 실험 표시). 피에조 294 Hz 확인 등.
- 이 lab부터 영상은 YouTube 대신 GitHub.
