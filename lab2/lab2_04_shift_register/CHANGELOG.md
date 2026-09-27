# 변경 기록

## v2.0.1 — 2026-09-13

- LAB1·LAB2 공통 단일 프로젝트 템플릿. 빈 RTL·TB·XDC와 기존 세 작업을 유지한다.
- clone 예시에 고정 태그와 작업 브랜치 생성을 명시한다.
- slang-server 0.3.0에 맞는 `.slang/server.json`을 추가한다. 편집기는 `src`·`sim`을 탐색하며, 시뮬레이션 파일 목록은 학생이 `simulation.json`에 별도로 작성한다.
- slang 확장·서버 확인 및 버전 불일치 해결 절차를 추가한다. 개인 설치 경로와 서버 바이너리는 포함하지 않는다.
- Icarus 설치·PATH 확인을 명확히 한다. VS Code는 Icarus, Vivado GUI는 XSim을 사용한다.
- `LAB1.code-workspace`와 `tools/lab1.py` 이름은 기존 교안과 호환되도록 유지한다. workspace의 `tasks.version: "2.0.0"`은 VS Code 스키마 버전이다.

## v2.0.0

- 완성 예제 없이 학생이 직접 작성하는 단일 프로젝트 틀과 Icarus 실행기를 제공한다.
