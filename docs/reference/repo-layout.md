# 저장소 구조

```
UOS_ece2/
  README.md                 Lab별 실험 영상 링크 (Lab1·2는 YouTube 재생목록, Lab3부터 GitHub README)
  03.LAB0_OT_0907.pdf       OT 자료(보고서 형식·출처 규칙). untracked
  docs/                     이 인수인계 문서
  lab1/  lab1_0K_*/ (10개), pdf/ (교안), report/pre, report/results
  lab2/  lab2_0K_*/ (8개), pdf/, reports/pre, reports/final, AGENTS.md   ← lab2만 reports(복수)
  lab3/  lab3_0K_*/ (7개), pdf/, report/pre, report/final(video/)
  lab4/  lab4_01_mult_4bit, lab4_02_bcd_conv, stm32_lab, stm32_0_hostsim, manual/, pdf/STM32_4week_plan.pdf, report/{pre,final}
  lab5/  lab5_01_piano, lab5_02_traffic, lab5_03_adc(+board_fix/), stm32_lab, stm32_1_hostsim, report/{pre,final}
  lab6/  lab6_01_servo(+variants/), lab6_02_sram, lab6_03_dac, lab6_04_uart_led, stm32_lab, stm32_2_hostsim, report/pre
  project/planning/         기획 PPT (untracked)
```

## FPGA 실습 폴더 (fpga-lab-template v2.0.2 기반)

```
labN_0K_<이름>/
  src/*.v                  RTL
  sim/tb.sv, tb_view.sv    조교 TB(또는 직접 작성), 보고서 그림용 TB
  constraints/<top>.xdc    LVCMOS33, create_clock 20.000 (clk_50mhz = B6)
  simulation.json          {"sources": [...], "testbench": "sim/tb.sv", "simulation_top": "tb"}
  tools/fpga_lab.py        템플릿의 Icarus 실행기 (lab1·2는 lab1.py)
  tools/build_bitstream.tcl  (lab1~4) 실험별 Vivado 빌드. lab5부터는 report/pre/tools/build_vivado.tcl로 일괄
  bitstream/<top>.bit      git에 올림 (lab3: BUILD_INFO.txt 동봉)
  evidence/vivado/         (lab3·4) 리포트
  FPGA.code-workspace      (lab1·2는 LAB1.code-workspace)
  build/ vivado/ .Xil/     gitignore
```

- 템플릿: `git clone --branch v2.0.2 https://github.com/Glaysia/fpga-lab-template.git <폴더>` 후 **`.git` 삭제**.
- 폴더 번호 = LAB 안의 실험 순서(교안의 교육 번호 아님).
- 공통: 50 MHz 단일 클록, clock-enable 카운터, 버튼은 2FF 동기화 + one-pulse.

## STM32 폴더

- `stm32_lab/`: 조교 프로젝트 `Glaysia/ece2_474` **v1.1.0**(커밋 `dd94f01047aebdece09b9620c66e9b179403e5c9`) 사본, `.git` 삭제. 고치는 파일은 `Core/Src/ece2_474_routine.c` 하나.
  lab마다 이전 lab의 stm32_lab을 복사하고 routine.c를 원본으로 되돌린 뒤 이번 과제를 쓴다. `docs/`에 조교 매뉴얼(STM32_0~3.md, FPGA_additional.md) 사본.
- `stm32_K_hostsim/`: `hostsim.c`, `mock/stm32g4xx_hal.h`, `run_hostsim.sh`, `results/`, `variants/`. 자세히는 [stm32.md](stm32.md).

## 보고서 폴더

```
report/pre/
  build_labN_report.py   docx 생성기 (인자: 커밋 해시)
  make_figures.py        그림 생성 (Pillow)
  LAB<N>_예비보고서.docx
  qa_render/             LibreOffice로 렌더한 PDF
  images/{block,vivado,hostsim,theory}/
  captures/              Vivado 전체 화면 캡처 원본(2560x1440)
  logs/                  icarus·xsim 로그, Vivado rpt, stm32_arm_build.txt, stm32_routine.diff
  tools/                 run_icarus.sh, run_xsim.sh, build_vivado.tcl, capture_xsim.ps1
report/final/
  build_labN_final.py, make_figures.py, LAB<N>_결과보고서.docx, qa_render/
  images/{board,meas}/, data/*.csv
  videos/  labN_fpga_0K_*.mp4, labN_stm32_0K_*.mp4, thumb/, README.md, original/(gitignore)
```
