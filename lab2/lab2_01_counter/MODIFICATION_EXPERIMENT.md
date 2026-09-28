# 수정실험 기록 — 4비트 카운터

## 교안 지시

교안 `../pdf/05.LAB2_01_COUNTER_VIVADO.pdf` 35–40쪽은 정상실험 파형을 열고 `clk`, `rst`, `enable`, `down`, `value[3:0]`를 관찰한 뒤 결과를 보고서에 넣도록 안내하며, 이 PDF에는 별도의 수정실험 항목이 없다. 수정실험 지시는 공통 교안 `../pdf/05.LAB2_00_START.pdf` 14쪽(11 · 업/다운 카운터)에 있다.

> 수정 실험: 증가량을 1에서 2로 바꾼다. 첫 증가 에지의 기대값과 실제값을 비교한 뒤 복구한다.

## 변경과 예상 동작

- 변경 RTL: `src/counter4.v`의 증가식 `value <= value + 4'd1`을 `value <= value + 4'd2`로 잠시 바꿨다. 감소식은 그대로 두었다.
- 테스트벤치: `sim/tb_counter4.sv`는 바꾸지 않았다. 리셋 해제 뒤 첫 증가 에지에서 `value=1`을 기대한다.
- 관찰 신호: `clk`, `rst`, `enable`, `down`, `value[3:0]`.
- 예상 실패: 5 ns 에지에서 리셋으로 `value=0`이 된 뒤 6 ns에 `rst=0`, `enable=1`, `down=0`이 된다. 15 ns 상승 에지에서 변경 회로는 0+2=2를 저장하고, TB는 다음 ns인 16 ns에 1을 기대하므로 첫 `up including 15 to 0` 검사에서 중단된다.

## 실행 결과

| 상태 | 결과 |
|---|---|
| 정상 기준 | `LAB2_PASS counter4 checks=36`, 356 ns 종료 (`evidence/normal/`) |
| 수정 | `LAB2_FAIL up including 15 to 0 time=16000` — 기대 1, 실제 2 (`evidence/modified/`) |
| 복구 | `LAB2_PASS counter4 checks=36`, 356 ns 종료 (`evidence/recovered/`) |

수정 실행과 복구 실행은 2026-09-28 Windows의 Icarus Verilog 12.0(`iverilog -g2012 -Wall`, `vvp -N`)으로 수행했다. 저장소의 `src/counter4.v`는 변경하지 않고, 증가식만 바꾼 사본(`evidence/modified/source/src/counter4.v`)을 원본 TB와 함께 컴파일했다. 수정 VCD는 16 ns에서 중단되므로 첫 증가 에지 결과인 `value=2`까지만 담는다.

| 항목 | 기록 |
|---|---|
| 정상 캡처 | `evidence/normal/normal_screenshot.png` — `lab2/images`의 2026-09-20 22:49:39 캡처 |
| 정상 로그·파형 | `evidence/normal/current_normal_simulation.log`, `evidence/normal/current_normal_wave.vcd`; 재현용 입력은 `evidence/normal/source/` |
| 수정 로그·파형 | `evidence/modified/simulation.log`, `evidence/modified/wave.vcd`, `exit_status.txt`=1 |
| 복구 로그·파형 | `evidence/recovered/simulation.log`, `evidence/recovered/wave.vcd`, `exit_status.txt`=0 |
| 기존 자료 | 기존 `evidence/normal/wave.vcd` 및 `counter4_normal_waveform.png`는 덮어쓰지 않고 보존 |
