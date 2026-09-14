# FPGA LAB1 — 직접 작성하는 프로젝트 틀

**프로젝트 하나, workspace 하나입니다.** 모든 실습은 같은 저장소를 새 이름으로 clone하고 PDF를 보며 Verilog·테스트벤치·핀 제약을 직접 작성합니다. 완성 회로와 예시 프로젝트는 들어 있지 않습니다.

## 1. 새 프로젝트 만들기

```sh
git clone https://github.com/Glaysia/fpga-lab-template.git new_project_name
cd new_project_name
code LAB1.code-workspace
```

`new_project_name`을 이번 실습 이름으로 바꾸세요. 다음 회로도 같은 URL을 다른 폴더 이름으로 clone합니다. 고정된 수업 버전은 clone 명령에 `--branch v2.0.0`을 추가하면 됩니다.

VS Code 메뉴로 열 때는 **File → New Window → Open Workspace from File... → 방금 만든 폴더의 LAB1.code-workspace**를 선택합니다.

## 2. 파일 세 개부터 작성하기

| 열 파일 | 직접 작성할 내용 |
|---|---|
| `src/design.v` | 입력·출력, 모듈 선언, 회로 동작 |
| `sim/tb_design.v` | DUT 연결, 입력 자극, 예상값 검사, 파형 덤프, 종료 |
| `constraints/pins.xdc` | 보드 핀 표에 맞는 PACKAGE_PIN·IOSTANDARD·get_ports |

세 파일은 주석만 있는 상태입니다. **PDF의 코드를 보고 입력하고 File → Save All을 누르세요.** 처음부터 시뮬레이션이 성공하지 않는 것이 정상입니다.

- 파일명을 바꾸려면 Explorer에서 파일 우클릭 → Rename. `simulation.json`의 `sources`와 `testbench`도 같은 이름으로 수정합니다.
- `simulation_top`에는 **TB의 module 이름**을 적습니다. 기본 이름은 `tb_design`이며, 설계 top과 구분합니다.
- 하위 모듈을 만들면 `src/`에 저장하고 `sources` 배열에 추가합니다. `.v`와 `.sv`를 사용할 수 있습니다. 나열한 파일만 컴파일합니다.
- TB에는 `wave.vcd`를 만드는 `$dumpfile`·`$dumpvars`, 입력을 바꾸는 시간 간격과 `$finish`를 작성합니다. 잘못된 출력은 `$fatal`로 검출하세요. 실행기는 정답 코드를 넣거나 기대값을 대신 계산하지 않습니다.
- XDC는 기능 시뮬레이션의 입력이 아닙니다. 포트·핀 대응은 구현 도구와 실제 보드에서 별도로 확인합니다.

## 3. 실행 준비

Python 3.10 이상, Git, VS Code, **Icarus Verilog의 `iverilog`·`vvp`**가 필요합니다. VS Code 추천 확장인 Verilog/SystemVerilog 도구와 VaporView도 설치합니다. 이 사전 시뮬레이션에는 Vivado가 필요하지 않습니다.

- **Windows:** Python을 설치할 때 PATH 등록을 선택합니다. [OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build)의 Windows 배포를 풀고 `bin`을 PATH에 추가한 뒤 VS Code를 다시 엽니다. 실행 파일·경로는 설치한 배포 기준으로 확인하세요.
- **Linux/WSL:** Icarus를 설치하거나 OSS CAD Suite의 Linux 배포를 사용합니다. Ubuntu에서는 `sudo apt install python3 git iverilog`로 준비할 수 있습니다. WSL을 쓰면 VS Code의 WSL 창에서 프로젝트를 열어 Linux의 Python·Icarus로 실행하세요.
- **macOS ARM64:** 해당 아키텍처의 OSS CAD Suite 배포 또는 패키지 관리자로 Python·Git·Icarus를 설치하고 `bin`을 PATH에 등록합니다. [Icarus 공식 설치 안내](https://steveicarus.github.io/iverilog/usage/installation.html)를 참고하세요.

Windows 터미널에서는 `python --version`, Linux/macOS에서는 `python3 --version`을 확인합니다. 이어서 `git --version`, `iverilog -V`, `vvp -V`가 실행되어야 합니다. 도구가 없다는 오류는 설치·PATH를 고친 뒤 새 VS Code 창에서 재확인하세요.

### 추천 확장 설치

왼쪽 Extensions 아이콘을 누르고 검색창에 `@recommended`를 입력하세요. workspace에서 추천한 확장의 Install을 누릅니다.

| workspace 추천 확장 | 식별자 | 용도 |
|---|---|---|
| [slang](https://marketplace.visualstudio.com/items?itemName=hudson-river-trading.vscode-slang) | `hudson-river-trading.vscode-slang` | Verilog/SystemVerilog 편집·진단·코드 탐색 |
| [VaporView](https://marketplace.visualstudio.com/items?itemName=lramseyer.vaporview) | `lramseyer.vaporview` | VCD 파형의 신호·시간·값 확인 |
| [vscode-pdf](https://marketplace.visualstudio.com/items?itemName=tomoki1207.pdf) | `tomoki1207.pdf` | 코드 옆에서 PDF 교안 열기 |

Windows에서 WSL로 실습한다면 [WSL](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl) (`ms-vscode-remote.remote-wsl`)도 별도로 설치하세요. HDL·파형 확장은 WSL 창에서 필요할 경우 **Install in WSL**로 설치합니다. WSL을 사용하지 않는 Windows·Linux·macOS에는 이 추가 확장이 필요하지 않습니다.

확장을 설치해도 Python·Icarus 실행 파일이 자동으로 준비되는 것은 아닙니다. 앞의 도구 설치와 01 Check tools도 수행해야 합니다.

## 4. 저장 → 시뮬레이션 → 파형 → 수정

**Terminal → Run Task...**에서 차례로 선택합니다.

1. **01 Check tools** — Python·Git·Icarus의 버전과 경로를 확인합니다.
2. **02 Simulate** — `simulation.json`에 적은 자기 RTL·TB를 컴파일하고 실행합니다.
3. **03 Open waveform** — 이번 실행의 `build/sim/wave.vcd`를 엽니다. 텍스트로 보이면 탭 우클릭 → Reopen Editor With... → VaporView를 선택합니다.

파형에서 입력·출력을 추가하고 Zoom Fit과 커서로 진리표와 비교합니다. 소스나 TB를 수정한 뒤에는 저장하고 **02를 다시 실행**하세요. 결과가 갱신되면 파형도 다시 열어 확인합니다.

`SIMULATED`는 컴파일·실행·새 파형 생성이 끝났다는 뜻입니다. **회로가 정답이라는 PASS 판정이 아닙니다.** 진리표·자기검사·파형을 직접 대조하여 실험 전 레포트에 설명하세요. 파일을 고치거나 최근 실행이 실패하면 03은 이전 파형을 현재 결과로 열지 않습니다.

실제 명령과 사용 파일은 터미널에 표시됩니다. 실행별 `compile.log`·`simulation.log`는 `build/sim/run-.../`, 최근 실행 상태는 `build/sim/result.json`에 남습니다. 실패 시 해당 로그에서 파일·줄을 찾아 수정합니다. 실패한 실행의 파형이 있다면 해당 run 폴더에서 오류 분석용으로 볼 수 있습니다.

터미널에서 직접 실행하려면 Windows에서는 `python tools/lab1.py check`, `python tools/lab1.py simulate`, `python tools/lab1.py wave`를 사용합니다. Linux/macOS에서는 `python3`로 바꿉니다. 긴 TB는 `simulate --timeout 600`처럼 실행 제한(초)을 조정할 수 있습니다.

## 5. 자신의 소스로 구현하기

**Vivado 실습:** New Project에서 자신이 작성한 `src/` 파일은 Design Sources, `sim/`의 TB는 Simulation Sources, `constraints/`의 XDC는 Constraints에 추가합니다. Copy sources 옵션을 끄고 실제 파일 경로와 두 top을 확인합니다. 이후 GUI에서 시뮬레이션·합성·구현·bit 생성·보드 기록을 진행합니다. 생성할 Vivado 프로젝트 폴더는 `vivado/`로 지정합니다.

**오픈소스 CLI 실습:** 같은 학생 소스를 Icarus로 검사한 뒤 교안에 따라 Yosys·nextpnr·프레임 변환으로 bit를 생성하고 **openFPGALoader**로 기록합니다. 앞의 세 task는 사전 시뮬레이션용이며, 이 템플릿에 부품별 chipdb·완성 통합 RTL·bit 빌드는 포함되어 있지 않습니다. 사용할 보드·도구·제약은 해당 실습에서 설정합니다. Vivado 설치나 Vivado bit를 CLI의 필수 조건으로 두지 않습니다.

## 6. 자신의 저장소에 제출하기

실험 전 레포트에는 예상값·직접 작성한 코드와 XDC 설명·사전 파형·수정 전후 결과를 넣습니다. 실험 후 레포트에는 구현·bit·실제 장치 기록·사진·영상과 결과 해석을 연결합니다. `reports/`와 `evidence/`를 필요할 때 만들고 자신의 자료를 넣으세요. 이 폴더의 사진·파형·로그는 `.gitignore`로 제외하지 않습니다.

자신의 GitHub 저장소를 만든 뒤 템플릿 원격과 제출 원격을 구분합니다. 아래 URL은 자신의 실제 저장소로 바꿉니다.

```sh
git remote rename origin template
git remote add origin https://github.com/YOUR_NAME/YOUR_PROJECT.git
```

VS Code Source Control에서 필요한 소스·레포트·증빙을 Stage → Commit한 뒤 자신의 `origin`으로 push합니다. `build/`의 캐시·도구 결과는 자동 제외됩니다. 제출할 로그·파형은 해당 실행의 파일을 `evidence/`로 복사하고 소스 커밋을 함께 기록하세요.

완성 예시와 강의자료는 [강의 저장소](https://github.com/Glaysia/ece2_26_2_2/tree/daily/0910)에서 별도로 관리합니다. 예시 소스를 찾아 복사하는 것은 허용하지만 변경한 코드와 파형을 스스로 설명해야 합니다.
