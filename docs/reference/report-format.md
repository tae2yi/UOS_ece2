# 보고서 형식

## OT가 정한 요건 (`03.LAB0_OT_0907.pdf` 31~37쪽)

- 보고서 종류: LAB1~LAB7 실험 전 7개 + 실험 후 7개, 프로젝트 제안서·계획서·결과보고서. **개인별** 작성·제출. 보고서당 10점, 요건 미충족 항목당 −1, 내용 미비 −1, 표절 −10.
- 공통 형식: **표지(이름·학번)**, 본문 **좌우 2단**, **PDF 제출**. 설계 목표·방법, 핵심 코드·회로 구조와 검증 결과, 예상과 실제 결과 비교, 문제 해결 과정과 결론,
  **허용된 출처 1개 이상 인용(본문 표시와 참고문헌 대응)**.
- 소스: 보고서에는 핵심 코드, 전체는 GitHub. **저장소 주소, 제출 버전의 태그와 커밋 해시** 기재.
- 실험 전(LAB1~3): 모든 실험, 실험별 설계·핵심 코드·입력 조건·예상 결과, 시뮬레이션 파형 스크린샷과 일치 여부 설명.
- 실험 후(LAB1~3): 모든 실험의 Vivado 시뮬레이션 파형과 해석, 조교가 고른 2개 실험의 보드 사진(사진마다 실험 번호·입력 조건·확인한 동작), 예상/실제 비교, 수정·재검증.
- STM32 주차(LAB4~): `STM32_4week_plan.pdf` 요건도 같다(이름·학번, 2단, PDF, GitHub 주소·태그·커밋, 허용 출처).
- 제출: 실험 전 보고서 월요일 18:00, 실험 후 보고서 월요일 14:00.

## 인용 가능한 출처 (OT 36·37쪽) — 참고문헌 쓰기 전에 반드시 확인

| 종류 | 조건과 표기 |
|---|---|
| 위키 | **불가** |
| GitHub | **스타 10개 이상**. 주소·참조 버전 또는 커밋·확인일 |
| 교과서 | 저자·제목·판본·출판 정보 |
| 논문 | 저자·제목·학술지 또는 학회·연도·DOI 또는 URL |
| 일반 도서 | ISBN 있는 책. 저자·제목·출판 정보·ISBN |

- 직접 인용은 따옴표·인용문 형식 + 출처와 쪽수. 요약·바꿔 쓴 내용에도 출처 표시. 본문 [1]과 목록 대응.
- **넣지 않는 것**: 자기 예비보고서, 교안·조교 매뉴얼(「STM32 실습 매뉴얼」 등), 조교 저장소 `Glaysia/ece2_474`, `fpga-lab-template`(스타 10개 미만). 이들은 "소스 출처" 표에만.
- 데이터시트(예: lab5 결과 [4] AD7908)는 OT 목록에 딱 맞지 않는다 → 사용자에게 확인 받은 적 없음. 가능하면 교과서·ISBN 도서·논문·STM32CubeG4로 대체.

### 지금까지 쓴 참고문헌 (재사용)

```
Joseph Yiu, The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors, 3rd ed., Newnes, 2013. ISBN 978-0-12-408082-9.
M. Morris Mano and Michael D. Ciletti, Digital Design: With an Introduction to the Verilog HDL, VHDL, and SystemVerilog, 6th ed., Pearson, 2018. ISBN 978-0-13-454989-7.
Sarah L. Harris and David Harris, Digital Design and Computer Architecture: ARM Edition, Morgan Kaufmann, 2015. ISBN 978-0-12-800056-4.
STMicroelectronics, STM32CubeG4 MCU Firmware Package (stm32g4xx_hal_uart.c 등). https://github.com/STMicroelectronics/STM32CubeG4
```
ISBN과 인용 내용은 책과 대조하지 않았다(lab4 보고 때 알림).

## docx 레이아웃 (python-docx, `build_lab*_report.py`의 헬퍼)

- A4(21 × 29.7 cm), 여백 좌우·위 1.8 cm, 아래 1.7 cm. 1쪽 표지는 1단 섹션, 본문은 새 섹션 2단(간격 425 twip).
- 글꼴 **Nanum Gothic**, 코드는 Consolas. 본문 10 pt(줄간격 1.12), 제목1 15 pt, 제목2 11.5 pt, 캡션 8 pt 굵게, 표 7~7.4 pt. 색 NAVY `1F4E78`.
- 표지: "LAB<N> 예비 보고서"/"LAB<N> 결과 보고서"(25 pt) + 부제(이번 주 주제, 12 pt 기울임) + `과목 전자전기컴퓨터설계실험 2` / `제출일` / `성명 김태이` / `학번 2023440158`.
- 바닥글: "LAB<N> 실험 전 보고서 · <쪽번호>".
- 한 단 폭 3.22 inch(약 8 cm), 그림 폭 3.18 inch. **그림은 폭 1000 px 안팎, 글자 20 px 이상**으로 그려야 읽힌다(1800 px·25 px로 그렸다가 다시 만든 적 있음).
- 코드 블록: 6.8 pt, **한 줄 63자까지**(`CODE_MAX`). 넘으면 `add_code`가 예외 → 소스 파일 자체를 줄바꿈해서 보고서와 소스를 일치시킨다(동작 동일 확인 후).
- 코드 블록·표 밑에 `GitHub: <링크>` 줄(`add_link_line`, `gh(path, first, last)` → `.../blob/<commit>/<path>#Lx-Ly`).
- 주요 헬퍼: `add_heading, add_text, add_table(headers, rows, widths), add_code, add_figure(path, caption, number) → 다음 번호, bullets, column_break, spacer`.
- docx 메타: title, subject, author='김태이'.
- 확인: LibreOffice로 `qa_render/*.pdf` 렌더 → 페이지 이미지로 넘침·잘림 확인.

## 분량 참고

lab4 예비 8쪽, lab5 결과 8쪽, lab6 예비 11쪽, lab4 결과 7쪽.
