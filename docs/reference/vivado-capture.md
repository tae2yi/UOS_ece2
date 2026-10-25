# Vivado 파형 GUI 캡처

결과보고서는 "Vivado 시뮬레이션 파형"이 요건이고, 사용자는 **Vivado를 직접 띄워 캡처**하길 원한다. 이 PC에서 동작한 방법.

1. 스크래치(영문 경로) 폴더에 `src/*.v`, `sim/<tb>.sv` 복사 → `xvlog -sv *.v <tb>.sv` → `xelab -debug typical <tb> -s tb_sim`.
2. 배치 실행 Tcl: `log_wave -r /`, `add_wave -radix <bin|hex|unsigned> /<tb>/<신호>` …, `run all`(또는 `run 460 ns`), `save_wave_config <tb>.wcfg`, `exit`.
   **stdin을 `/dev/null`로** 주지 않으면 `xsim%` 프롬프트에서 멈춘다. → lab6 `report/pre/tools/run_xsim.sh`가 이 과정을 자동화.
3. GUI 캡처: `powershell -File lab6/report/pre/tools/capture_xsim.ps1 -WorkDir <xsim 폴더> -Wcfg <tb>.wcfg -Out <png>`
   - `xsim tb_sim.wdb -gui -view <wcfg>`를 띄워 창 최대화 → 대기(`-SettleSeconds 12`) → **PrintWindow(PW_RENDERFULLCONTENT)**로 창 내용만 받아 GetWindowRect 위치에 그림 → 종료.
   - 다른 창이 가려도 된다. 예전 `CopyFromScreen` 방식은 사용자가 PC를 쓰는 중이면 다른 창이 찍혔다(lab6에서 8장 중 5장). **lab6 스크립트를 복사해 쓸 것.**
   - `SetProcessDPIAware` 필요. 결과는 2560×1440 전체 화면 크기.
4. **동시에 두 개 돌리지 말 것.**
5. wcfg의 zoom 설정은 무시되고 항상 전체 구간이 보인다 → 확대가 필요하면 **run 길이를 줄인다**(또는 보기용 `tb_view.sv`를 짧게 작성).
6. 그대로는 한 단에서 글자가 너무 작다 → `make_figures.py`의 `crop_vivado()`가 이름 열(x 947~1204)과 파형(1208~2356)을 잘라 **시간축 반씩 두 줄**로 쌓는다.
   좌표: `TOP_Y 322, ROW_Y 356, ROW_H 36`(신호 한 행 36 px), 신호 행 수를 표에 적는다. 창을 작게 해서 캡처하는 방법은 파형 영역이 너무 줄어 못 썼다.
7. 캡처 도중 Vivado 창이 화면에 떴다 닫힌다 → 사용자에게 미리 알리면 좋다.
