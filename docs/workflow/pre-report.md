# 예비보고서(실험 전 보고서) 만드는 절차

LAB4~LAB6에서 실제로 해 온 순서다. 가장 최근 예시인 **lab6**를 복사해서 시작하면 된다.
도구 경로는 [../reference/environment.md](../reference/environment.md), 형식은 [../reference/report-format.md](../reference/report-format.md).

## 0. 시작 대화

사용자는 보통 "labN 예비보고서 작성하려고 해. 혹시 조교 깃허브에 관련자료가 있는지 확인해줄래?"로 시작한다.

1. 조교 저장소 <https://github.com/Glaysia/ece2_474>의 `docs/index.md` 주차 표에서 해당 날짜 문서를 찾는다
   (10/12 STM32_0, 10/19 STM32_1, 10/26 STM32_2, 11/2 STM32_3). `docs/FPGA_additional.md`에 그 주 FPGA 교재 실습(Verilog 소스·TB)이 절별로 있다.
   로컬에 최신 사본이 `lab6/stm32_lab/docs/`에 있지만, 조교가 갱신했을 수 있으니 웹(또는 clone)으로 다시 확인한다.
2. 이번 주 MCU 과제, FPGA 실습, 배선·핀 변경, 퀴즈 공지 등을 표로 요약해 보고하고 진행 범위를 제안한다.
3. 사용자가 "그렇게 진행하자" 하면 아래를 진행한다. 중간 확인 없이 끝까지 하고 마지막에 보고한다.

## 1. 폴더 만들기

```
labN/
  labN_01_<이름>/ ...      FPGA 실습마다 하나 (fpga-lab-template v2.0.2 구조, .git 삭제)
  stm32_lab/               이전 lab의 stm32_lab을 복사 → Core/Src/ece2_474_routine.c만 원본으로 되돌리고 이번 과제 작성
  stm32_K_hostsim/         PC에서 MCU 코드 돌리는 호스트 시뮬레이션 (K = STM32_K)
  report/pre/              보고서 생성 스크립트·그림·로그
  .gitignore               (lab5/.gitignore 복사: lock 파일, __pycache__, report/final/videos/original/)
```

- FPGA 프로젝트 폴더 구조와 `simulation.json`은 [../reference/repo-layout.md](../reference/repo-layout.md) 참고. lab5·6은 이전 lab 프로젝트 폴더를 복사해서 `src/ sim/ constraints/`만 바꿨다.
- 이름은 LAB 안의 순서: `lab6_01_servo`, `lab6_02_sram`, `lab6_03_dac`, MCU 연동 FPGA는 `lab6_04_uart_led`.
- 조교 소스는 원본 그대로 두고, 고칠 것이 있으면 따로 모듈을 붙이거나(`button_pulse.v`) 대비안을 `variants/`에 둔다.

## 2. MCU(STM32) 코드와 검증

1. `stm32_lab/Core/Src/ece2_474_routine.c`에 과제 작성. 여러 과제는 매크로로 고른다(lab6: `STM32_2_TASK=5|6`).
2. Arm GCC 빌드: [../reference/stm32.md](../reference/stm32.md)의 명령으로 `cmake --preset Debug && cmake --build --preset Debug`.
   빌드 출력은 `report/pre/logs/stm32_arm_build.txt`, 원본 대비 diff는 `logs/stm32_routine.diff`로 저장(보고서에 링크).
3. 호스트 시뮬레이션: `stm32_K_hostsim/`에 HAL 대역 헤더(`mock/stm32g4xx_hal.h`)와 `hostsim.c`를 두고, **보드용 routine.c를 고치지 않고** PC gcc로 컴파일해
   시나리오(누름·떨림·길게 누름·wrap, UART 입력 바이트 등)를 CSV/텍스트로 `results/`에 남긴다. `run_hostsim.sh` 하나로 전부 재실행되게 한다.
4. 떨림 등 위험이 보이면 대안 코드를 `variants/`에 두고 보고서에 "보드에서 이 현상이 나오면 교체"로 적는다.

## 3. FPGA 시뮬레이션

- 조교 TB(`sim/tb.sv`) 외에 보고서 그림용으로 핵심 구간만 보여 주는 `sim/tb_view.sv`를 직접 작성한다.
- Icarus: `report/pre/tools/run_icarus.sh` → `logs/<proj>_<tb>_icarus.txt` (PASS 줄 확인).
- Vivado xsim: `tools/run_xsim.sh <작업폴더>` → WDB·WCFG 생성, `logs/<proj>_<tb>_xsim.txt`. 작업 폴더는 스크래치(한글 경로·저장소 오염 방지).
  `waves()` 함수에 프로젝트별 신호·radix를 적는다.
- MCU–FPGA 연동 과제는 호스트 시뮬레이션이 UART3로 보낸 바이트 파일(`results/*_uart3.hex`)을 FPGA TB가 그대로 읽게 해 전체 흐름을 잇는다(lab6).

## 4. Vivado 구현과 bitstream

- `vivado -mode batch -source report/pre/tools/build_vivado.tcl -tclargs <labN 폴더>` (비프로젝트 모드, part `xc7s75fgga484-1`).
  `simulation.json`의 sources를 읽어 합성 → opt/place/route → utilization·timing·drc 리포트를 `logs/`에, bitstream을 `<proj>/bitstream/<top>.bit`에.
- 핀이 정해지지 않은 설계는 bit 플래그 0으로 두고 배치·배선까지만(보고서에 "핀 미정"). 타이밍 WNS·DRC 결과를 보고서 구현 절에 적는다.
- XDC 핀은 [../reference/board-combo2.md](../reference/board-combo2.md)에서 확인된 값만 쓰고, 추정이면 XDC 주석과 보고서에 "추정"이라고 쓴다.

## 5. 파형 캡처와 그림

1. Vivado GUI 캡처: `report/pre/tools/capture_xsim.ps1 -WorkDir <xsim 폴더> -Wcfg <tb>.wcfg -Out report/pre/captures/<proj>_<tb>.png`
   (자세한 방법·주의는 [../reference/vivado-capture.md](../reference/vivado-capture.md)). **동시에 두 개 돌리지 말 것.**
2. `report/pre/make_figures.py` 실행 → `images/vivado/`(캡처를 이름 열 + 시간축 반씩 두 줄로 재배치), `images/block/`(블록도), `images/theory/`(타이밍 개념도), `images/hostsim/`.
   Pillow로 직접 그린다(matplotlib 없음). 폭 1000 px 안팎, 글자 20 px 이상. `VIVADO` 표에 (파일, 신호 행 수)를 적는다.

## 6. 보고서 생성

1. 이전 lab의 `build_labN_report.py`를 복사해 내용을 바꾼다(docx 헬퍼는 그대로).
2. `python build_labN_report.py` → `LAB<N>_예비보고서.docx`. 인자로 커밋 해시를 주면 GitHub 링크가 그 커밋을 가리킨다(생략 시 `master`).
3. LibreOffice로 PDF 렌더: `soffice --headless --convert-to pdf --outdir qa_render LAB<N>_예비보고서.docx` → 페이지를 이미지로 보고 넘침·잘림·빈 칸을 확인.
4. 장 구성(lab6 예): 1 범위와 결론(요약 표) → 2 실험 환경과 검증 방법 → 3 소스 출처와 실행 스냅샷 → 이론(UART 등) → MCU 과제별(요구·설계·핵심 코드·예상 결과·빌드·보드에서 확인할 항목)
   → FPGA 실습별(목적과 원리·블록도·시뮬레이션 결과(파형+해석)·구현 결과·보드에서 확인할 항목) → 예상 결과 정리와 실험 계획(순서·기록할 것 표) → 참고 문헌.
5. 표지 제출일은 실험 날짜(월요일).

## 7. 보고와 커밋

- 사용자에게: 보고서 경로(docx, qa_render PDF), 검증 결과 표, "실험 전에 알아둘 것"(배선·DIP SW·타이밍 위험), "부탁드릴 것"(핀 표 사진 등), 미커밋 상태를 보고.
- "커밋하고 링크를 그 해시로 고정해줘" → [git.md](git.md)의 2단계 커밋.
- 맥 실험 매뉴얼이 필요하면 [lab-manual.md](lab-manual.md).
