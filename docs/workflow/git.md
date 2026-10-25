# git 사용 방식

- 원격: `origin = https://github.com/tae2yi/UOS_ece2`, 브랜치 `master` 하나. 맥에서도 같은 저장소를 pull 한다.
- 커밋 작성자: 사용자 git 설정 그대로(과거 요약 기준 `vizatae <ip9368@naver.com>`). 따로 바꾸지 않는다.
- 커밋·push는 사용자가 요청할 때. 요청에는 바로 응한다("커밋하고 푸시해줘").
- 다른 세션이 다른 lab을 동시에 고칠 수 있으므로 **자기 lab 폴더만** `git add labN`. 루트의 `03.LAB0_OT_0907.pdf`, `project/`는 요청 없으면 올리지 않는다.
- 한글 파일 이름이 `git status`에서 `"\352..."`로 보이면 `git -c core.quotepath=off status`.

## 커밋 메시지 형식

`labN: <무엇을 했는지 한국어로>` — 예:
- `lab6: STM32_2 과제5~7, FPGA 서보·SRAM·DAC와 예비보고서`
- `lab6: 예비보고서의 GitHub 링크를 커밋 cb8ab23으로 고정`
- `lab5: 보드 실험 영상 5개와 README, 영상 측정값·보드 사진 추가`
- `lab5: 결과보고서 참고문헌에서 예비보고서 항목 제거`

## 링크를 커밋 해시로 고정하는 2단계 커밋

보고서 안 GitHub 링크가 `master`를 가리키면 나중에 내용이 바뀌므로 제출용은 해시로 고정한다.

1. 작업 전체 커밋 → 해시 `H` 확인(`git rev-parse --short HEAD`).
2. 예비: `python build_labN_report.py H` / 결과: 스크립트의 `CODE_COMMIT = '<H 전체>'` 수정 후 빌드. qa_render PDF도 다시 만든다.
3. 문서 안 링크가 모두 `H`를 가리키고 `master` 링크가 남지 않았는지 확인(줄 번호 링크 `#Lx-Ly`는 그 커밋의 실제 파일과 대조).
4. `labN: 예비보고서의 GitHub 링크를 커밋 H로 고정` 으로 두 번째 커밋 → push.

## 태그

- `lab3-final` 하나 있다. lab4 결과보고서는 본문에 `lab4-final`을 적었지만 태그는 아직 없다([../STATUS.md](../STATUS.md)). lab5는 태그 없이 커밋 해시만 적었다.
- OT 요건: 저장소 주소, **제출 버전의 태그와 커밋 해시**를 보고서에 기재.

## gitignore 요점

- FPGA 프로젝트마다 `.gitignore`: `/build/`, `/vivado/`, `.Xil/`, `*.jou` 등. **`bitstream/`은 올린다.**
- `labN/.gitignore`: Office lock 파일, `__pycache__/`, `report/final/videos/original/`.
- `qa_render/`(렌더 PDF)는 올라가 있다.
