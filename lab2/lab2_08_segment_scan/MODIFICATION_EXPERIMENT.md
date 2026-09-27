# 수정 실험 — 자리 blanking 제거

## 교안 지시와 출처

출처: [`05.LAB2_08_SEGMENT_SCAN_VIVADO.pdf`](../pdf/05.LAB2_08_SEGMENT_SCAN_VIVADO.pdf), 수정 실험 인쇄 쪽수 48, 파형 해설 쪽수 50. 두 페이지를 렌더링해 지시와 기대 결과를 시각적으로 확인했다.

교안은 정상 로그와 파형을 먼저 보관하고 자리 전환 blanking을 제거하되 TB 기대값은 유지하도록 한다. 이어 `02 Simulate`에서 실패 검사명과 시각을 확인하고 입력과 이전 상태를 계산한 다음 RTL을 복구해 전체 PASS를 확인한다. 해설은 `blank ? 8'h00 :` 부분을 제거하면 6 ns `reset blanks digit zero` 검사가 먼저 실패하고, 기대 `select=00` 대신 `01`이 나오며, 원복 후 194개 PASS와 1306 ns 종료를 확인하라고 명시한다.

## 변경과 예상 동작

- 변경 RTL: [`src/segment_scan8.v`](src/segment_scan8.v)에서 `select = blank ? 8'h00 : (8'b0000_0001 << index);` 대신 one-hot 선택식만 남겼다.
- 테스트벤치: [`sim/tb_segment_scan8.sv`](sim/tb_segment_scan8.sv)는 바꾸지 않았다. 리셋 중 `select=0`, `index=0`을 기대한다.
- 관찰 신호: `clk`, `rst`, `enable`, `digits[31:0]`, `index[2:0]`, `select[7:0]`, `segments[7:0]`.
- 예상 실패: 리셋 상승 에지 후 `index=0`이다. blank 조건을 없애면 첫 자리 선택 `select=8'h01`이 리셋 중에도 활성화되며, TB가 6 ns에 기대하는 `select=8'h00`과 다르다. 첫 체크에서 실패한다.

## 실행 결과

| 상태 | 결과 |
|---|---|
| 정상 기준 | `LAB2_PASS segment_scan8 checks=194`, 종료 1306 ns |
| blanking을 제거한 RTL | `LAB2_FAIL reset blanks digit zero time=6000` (6 ns); 기대 `00`, 실제 `01` |
| RTL 원복 | `LAB2_PASS segment_scan8 checks=194`, 종료 1306 ns |

Icarus 비 GUI 시뮬레이션으로 실행했다. 수정 RTL 실행은 TB의 `$fatal`로 예상된 첫 불일치에서 종료 코드 1을 반환한다. 로그와 실패 시점까지의 VCD를 별도 보관했다. RTL을 원복한 뒤 194개 검사가 모두 통과했다.

## 캡처와 재현 자료

- 정상 원본 스냅샷: [`evidence/normal/source/`](evidence/normal/source/) — RTL, TB, 설정, 제약.
- 정상 로그와 파형: [`evidence/normal/simulation.log`](evidence/normal/simulation.log), [`evidence/normal/wave.vcd`](evidence/normal/wave.vcd).
- 정상 스크린샷: [`evidence/normal/normal_screenshot.png`](evidence/normal/normal_screenshot.png). `lab2/images` 시간순 8번째 파일(2026-09-20 23:55:30)을 복사했다.
- 수정 RTL 스냅샷: [`evidence/modified/source/segment_scan8.v`](evidence/modified/source/segment_scan8.v). TB는 정상 원본 스냅샷과 동일하다.
- 수정 로그, VCD, 보고서용 파형: [`evidence/modified/simulation.log`](evidence/modified/simulation.log), [`evidence/modified/wave.vcd`](evidence/modified/wave.vcd), [`evidence/modified/waveform.png`](evidence/modified/waveform.png).
- 복구 로그와 파형: [`evidence/recovered/simulation.log`](evidence/recovered/simulation.log), [`evidence/recovered/wave.vcd`](evidence/recovered/wave.vcd).

수정 파형은 `index=0`, `select=01`, `segments=FC` 상태와 6 ns 실패를 보인다. 리셋 중 자리 선택이 켜진 것이 첫 실패 원인이라는 PDF 해설과 일치하며 해석상 불확실성은 없다. 작업 트리 RTL은 원복 상태다.
