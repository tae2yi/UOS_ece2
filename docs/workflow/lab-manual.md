# 맥에서 쓸 실험 매뉴얼 만들기

사용자가 요청할 때만 만든다(지금까지 lab4 한 번: `lab4/manual/LAB4_실험매뉴얼.html` → `.pdf`, 12쪽).

## 배경

실제 실험은 **M1 Pro MacBook**에서 `tae2yi/UOS_ece2`를 `git pull` 해서 진행한다. 맥에는 STM32CubeMX·CubeIDE, **Vivado 2026.1**이 있다(이 PC는 2025.2).
`build/`, `vivado/`는 git에 없으므로 맥에서 다시 만드는 방법을 함께 적는다. 저장소의 `.bit`는 2025.2로 만든 것.

## 만드는 법

- HTML로 쓰고 Edge 헤드리스로 PDF:
  ```
  "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --no-pdf-header-footer --print-to-pdf=<pdf 절대경로> file:///<html 절대경로>
  ```
- 구성(lab4): 1 오늘 할 일(순서표·준비물) → 2 맥 준비(VS Code 확장 방식과 터미널 방식, Icarus 설치) → 3 STM32 진행(예제·과제 절차, 예상값과 실제값 기록 칸)
  → 4 FPGA 진행(시뮬레이션, bitstream, 내려받기, 입력별 스위치·LED 표) → 5 관련 개념 → 6 결과보고서용 기록(찍을 것·적을 것·커밋·태그 명령) → 7 안 될 때(증상별).
- 맥 명령과 Vivado 2026.1 동작은 이 PC에서 검증할 수 없으므로 문서에 그렇게 적는다.
