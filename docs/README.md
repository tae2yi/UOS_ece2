# UOS_ece2 작업 문서 — 새 세션은 여기부터 읽는다

이 폴더는 Claude 세션의 대화 기록이 사라져도 다음 세션이 이 문서만 보고 바로 작업을 이어 가도록 만든 인수인계 문서다.
작성: 2026-10-21 (LAB6 예비보고서 커밋 직후). 이후 작업을 하면 [STATUS.md](STATUS.md)와 해당 lab 문서를 갱신한다.

## 한 줄 요약

서울시립대 **전자전기컴퓨터설계실험 2**(2026 2학기, 월 14:00~18:00) 수업의 실험 전(예비)·실험 후(결과) 보고서와 사전 실험(코드·시뮬레이션·bitstream)을
이 Windows PC에서 만들고, 사용자는 실제 실험을 **M1 Pro 맥북**에서 저장소를 pull 해서 진행한다.

- 사용자: **김태이**, 학번 **2023440158**, GitHub `tae2yi`, 저장소 <https://github.com/tae2yi/UOS_ece2> (브랜치 `master`)
- 로컬 저장소: `C:\ece2\UOS_ece2` (세션의 작업 폴더는 보통 `C:\ece2`)
- 장비: FPGA = HBE-Combo II-DLD, Spartan-7 **xc7s75fgga484-1** / MCU = **NUCLEO-G474RE**
- 사용자와는 **한국어**로 대화한다. 보고서도 한국어.

## 읽는 순서

| 순서 | 문서 | 내용 |
|---|---|---|
| 1 | [STATUS.md](STATUS.md) | 지금 어디까지 했고 다음에 무엇을 하는지, 미커밋·미확인 항목, 일정 |
| 2 | [RULES.md](RULES.md) | 사용자가 준 지시와 피드백 전부(어기면 다시 해야 함) |
| 3 | 작업 종류에 맞는 절차 | 아래 표 |
| 4 | 해당 lab 문서 | [labs/](labs/) |

| 하려는 일 | 절차 문서 |
|---|---|
| 예비보고서(실험 전 보고서) 작성 | [workflow/pre-report.md](workflow/pre-report.md) |
| 결과보고서(실험 후 보고서) 작성 | [workflow/final-report.md](workflow/final-report.md) |
| 맥에서 쓸 실험 매뉴얼 PDF | [workflow/lab-manual.md](workflow/lab-manual.md) |
| 커밋·푸시·링크 해시 고정 | [workflow/git.md](workflow/git.md) |
| 조별 프로젝트(미니 ATE) 기획 PPT | [project/mini-ate.md](project/mini-ate.md) |

## 참고 자료

| 문서 | 내용 |
|---|---|
| [reference/environment.md](reference/environment.md) | 이 PC의 도구 경로(PATH에 없음!), Python, Vivado, Icarus, ARM GCC, ffmpeg. **gitignore된 로컬 전용 문서** — 이 Windows PC에만 있고 GitHub·맥에는 없다 |
| [reference/repo-layout.md](reference/repo-layout.md) | 저장소 폴더 구조와 이름 규칙, FPGA 템플릿, STM32 프로젝트 |
| [reference/report-format.md](reference/report-format.md) | 보고서 형식(OT 요건, docx 레이아웃, 그림·코드 크기, 참고문헌 규칙) |
| [reference/vivado-capture.md](reference/vivado-capture.md) | Vivado 파형을 실제 GUI로 캡처하는 방법 |
| [reference/board-combo2.md](reference/board-combo2.md) | Combo II-DLD 핀 번호(확인된 것/미확인), 내장 장치 |
| [reference/stm32.md](reference/stm32.md) | 수업 STM32 프로젝트(Glaysia/ece2_474), 빌드, 호스트 시뮬레이션 |
| [reference/course.md](reference/course.md) | 수업 일정, OT 요약, 조교 저장소 위치 |
| [history.md](history.md) | 세션별 작업 이력(날짜순) |

## 절대 잊으면 안 되는 것 (상세는 RULES.md)

1. 참고문헌에 **예비보고서·교안·조교 매뉴얼·조교 저장소(Glaysia/ece2_474)**를 넣지 않는다. 출처 규칙은 OT 파일(`03.LAB0_OT_0907.pdf`).
2. 정상 실험의 bitstream·프로젝트 파일은 실제 실습에 쓰므로 **손상시키지 않는다**(수정본은 별도 폴더·파일명).
3. 템플릿·수업 프로젝트를 clone 하면 **중첩 `.git`을 지우고** 올린다.
4. 보고서의 GitHub 링크는 커밋한 뒤 **그 커밋 해시로 고정**해서 다시 빌드·커밋한다.
5. 커밋·푸시는 사용자가 요청할 때 한다. Python·Vivado 등은 PATH에 없으니 [environment.md](reference/environment.md)의 경로를 쓴다.
6. 보고서는 python 스크립트(`build_*.py`)로 docx를 **생성**한다. docx를 손으로 고치지 말고 스크립트를 고쳐 다시 만든다.
