# 결과보고서(실험 후 보고서) 만드는 절차

lab4·lab5에서 한 방식. 가장 최근 예시는 **`lab5/report/final/`** (`build_lab5_final.py`, `make_figures.py`, `videos/README.md`).

## 0. 시작 대화

사용자: "labN 결과보고서 작성시작하자. 실습때의 영상은 /final/videos에 담아두었어. 순서대로 fpga1,2,3랑 stm 1,2야.
보고서에는 fpga랑 stm 모두 사진 들어가야해. 영상은 이름바꿔서 readme 통해 github에 올려줘"

→ 사용자가 넣은 휴대폰 원본(카카오톡/HEVC, 이름이 숫자)이 `labN/report/final/videos/`에 있다.

## 1. 영상 정리

1. ffmpeg 준비(PC에 없음): 스크래치에 `python -m pip install --target <scratch>/pylib imageio-ffmpeg` → `pylib/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-*.exe`.
2. **영상 내용을 보고 실험과 짝을 맞춘다**(파일 이름 순서가 사용자가 말한 순서와 다를 수 있음). 프레임 몇 장을 뽑아 확인하고, 다르면 보고 때 표로 알린다.
3. H.264로 재인코딩하고 이름을 바꾼다: `labN_fpga_0K_<이름>.mp4`, `labN_stm32_0K_task<번호>_<이름>.mp4` (예: `lab5_fpga_02_traffic.mp4`, `lab5_stm32_02_task4_pwm.mp4`).
4. 원본은 `videos/original/`로 옮긴다(`labN/.gitignore`에 `report/final/videos/original/`).
5. 썸네일 `videos/thumb/<같은이름>.jpg`.
6. `videos/README.md`: 제목 "# LAB N 보드 실험 영상", 촬영일·보드·bitstream 위치 설명, 표 `| 실험 | 영상(썸네일 링크 + 파일 링크, 길이) | 입력 조건 | 영상에서 확인한 동작 |`, 아래에 측정 방법 주석. lab5 README를 그대로 본뜬다.
7. 루트 `README.md`에 `- [Lab N 실험 영상](labN/report/final/videos/README.md)` 추가.

## 2. 측정값과 그림 (`make_figures.py <ffmpeg 경로>`)

- 영상 장면 → `images/board/*.jpg`: 보드 사진에 시각과 값을 적어 여러 장을 시트로(`sheet()`, `crop()`).
- 측정 → `data/*.csv`, `images/meas/*.png`. 지금까지 쓴 방법:
  - LED 켜짐/꺼짐 시각: 프레임마다 LED 영역 화소 밝기 → 에지 시각(30 fps, 1프레임 0.033 s). 설계 규칙으로 계산한 시각과 비교하는 타이밍 그림(`timing()`은 예비보고서 make_figures에서 import).
  - 피에조 음: 영상 음성 스펙트럼/고조파로 주파수.
  - 버튼 누름 시각: 클릭음(`clicks()`).
  - 사람이 읽은 값(LED 이진수, 오실로스코프 듀티)은 코드 안 표(`ADC_READ`, `PWM_READ`)에 적고 보고서·README에 "장면을 보고 읽은 값"이라고 밝힌다.
- 예비보고서의 Vivado 파형 그림(`../pre/images/`)을 재사용해 예상과 비교한다.

## 3. 보고서 생성 (`build_labN_final.py`)

- 예비보고서 모듈을 import 해서 docx 헬퍼를 그대로 쓴다:
  ```python
  CODE_COMMIT = '<영상·측정값·소스가 모두 들어간 커밋 전체 해시>'
  sys.argv = [sys.argv[0], CODE_COMMIT[:7]]
  sys.path.insert(0, str(HERE.parent / 'pre'))
  import build_labN_report as B
  ```
- 장 구성(lab5): 1 실험 범위와 결과 요약 → 2 실험 환경과 측정 방법(영상에서 값을 읽은 방법) → 실험별 장(설계와 사전 검증 / 보드 관찰(사진+표) / 예상과의 비교)
  → 토론(예상과 실제의 비교, 오차와 한계, 개선 방법) → 결론 → 제출 자료(저장소·커밋·폴더·영상 README·측정값 위치 표) → 참고 문헌.
- 각 사진에 실험 번호, 입력 조건, 확인한 동작을 쓴다. 예상과 다른 결과는 원인 분석(재현 시뮬레이션 등)과 "문제와 해결"을 쓴다. 원인을 확정 못 하면 "원인 추정"/"미확정".
- **참고문헌에 예비보고서·매뉴얼·조교 저장소 넣지 않기.** 예비보고서와의 비교는 서술로만.
- LAB1~3 형식(OT): 모든 실험의 Vivado 파형과 해석 + 조교가 고른 2개 실험의 보드 사진. LAB3은 시연이 07 UART 1개였고 영상 7개를 모두 README에 올렸다.

## 4. 렌더 확인, 커밋 순서

1. `soffice --headless --convert-to pdf --outdir qa_render LAB<N>_결과보고서.docx` → 페이지 이미지로 확인.
2. 커밋 순서(lab5): ① 영상·README·측정값·사진·make_figures 커밋(`4ff988d`) → ② 그 해시를 `CODE_COMMIT`에 넣고 보고서 빌드 → 보고서 커밋(`2ca573d`) → push. 사용자가 요청한 경우에만.
3. 보고 시: 보고서 경로, 영상 이름 대응표, 측정 결과 요약, 새로 발견한 문제, "직접 읽은 값"·추가한 참고문헌 등 확인해 달라는 것.
