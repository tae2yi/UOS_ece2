"""Run the student's explicitly listed files with Icarus; never supply a solution."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/sim"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs():
    config = ROOT / "simulation.json"
    cfg = json.loads(config.read_text(encoding="utf-8-sig"))
    top = cfg["simulation_top"]
    if not isinstance(top, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", top):
        raise ValueError("simulation_top에 TB 모듈명을 적으세요.")
    if not isinstance(cfg["sources"], list) or not cfg["sources"]:
        raise ValueError("sources에 작성한 RTL 파일을 등록하세요.")
    files = []
    for name, folder in [(s, "src") for s in cfg["sources"]] + [(cfg["testbench"], "sim")]:
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT / folder) or path.suffix not in (".v", ".sv"):
            raise ValueError(f"{folder}/ 아래의 .v 또는 .sv 파일을 지정하세요: {name}")
        if not path.is_file():
            raise ValueError(f"파일이 없습니다. 파일명과 simulation.json을 확인하세요: {name}")
        files.append(path)
    hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in [config, *files]}
    # Include local headers/data in the freshness check, without auto-compiling them.
    for folder in (ROOT / "src", ROOT / "sim"):
        for path in folder.rglob("*"):
            if path.is_file():
                hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    return top, files, hashes


def tool(name):
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"{name}을 찾을 수 없습니다. README의 설치·PATH 안내를 확인하세요.")
    return path


def execute(argv, cwd, log, timeout):
    print("RUN", subprocess.list2cmdline([str(x) for x in argv]), flush=True)
    with log.open("w", encoding="utf-8") as output:
        try:
            result = subprocess.run(argv, cwd=cwd, stdout=output, stderr=subprocess.STDOUT,
                                    timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            output.write("\nTIMEOUT: TB의 종료 조건을 확인하세요.\n")
            raise RuntimeError(f"실행 시간 초과: {log}") from None
    print(log.read_text(encoding="utf-8", errors="replace"), flush=True)
    if result.returncode:
        raise RuntimeError(f"종료 코드 {result.returncode}: {log}")


def check():
    out = ROOT / "build/check"
    out.mkdir(parents=True, exist_ok=True)
    print("Python", sys.version.split()[0])
    for name, flag in [("git", "--version"), ("iverilog", "-V"), ("vvp", "-V")]:
        execute([tool(name), flag], ROOT, out / (name + ".log"), 30)
    print("도구 확인 완료. 다음은 src/·sim/·constraints/의 파일을 직접 작성하세요.")


def simulate(timeout):
    OUT.mkdir(parents=True, exist_ok=True)
    # Clear the published wave even when a changed config or compilation fails.
    (OUT / "wave.vcd").unlink(missing_ok=True)
    run = OUT / ("run-" + uuid.uuid4().hex)
    run.mkdir()
    result = {"status": "RUNNING", "run": run.name, "functional_correctness": "NOT_ASSESSED"}

    def save():
        (OUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8")

    save()
    try:
        top, files, hashes = inputs()
        result["inputs_sha256"] = hashes
        save()
        execute([tool("iverilog"), "-g2012", "-Wall", "-I", str(ROOT / "src"),
                 "-I", str(ROOT / "sim"), "-s", top, "-o", str(run / "sim.vvp"),
                 *map(str, files)], run, run / "compile.log", timeout)
        execute([tool("vvp"), "-N", str(run / "sim.vvp")], run, run / "simulation.log", timeout)
        wave = run / "wave.vcd"
        if not wave.is_file():
            raise RuntimeError("새 wave.vcd가 없습니다. TB의 $dumpfile·$dumpvars를 확인하세요.")
        text = wave.read_text(encoding="utf-8", errors="replace")
        if "$enddefinitions" not in text or "$var " not in text:
            raise RuntimeError("신호가 기록된 VCD가 아닙니다. TB의 파형 덤프 설정을 확인하세요.")
        if not re.search(r"^#[1-9][0-9]*\s*$", text, re.M):
            raise RuntimeError("파형 시간이 진행되지 않았습니다. TB의 입력 간격·종료를 확인하세요.")
        if inputs()[2] != hashes:
            raise RuntimeError("실행 중 파일이 변경되었습니다. 저장 후 다시 실행하세요.")
        shutil.copy2(wave, OUT / "wave.vcd")
        result.update(status="SIMULATED", wave_sha256=digest(wave))
        print("시뮬레이션 실행 완료. 진리표·자기검사·파형으로 회로의 정답 여부를 확인하세요.")
        print("WAVE", OUT / "wave.vcd")
    except Exception as exc:
        result.update(status="FAILED", error=str(exc))
        raise
    finally:
        save()


def current_wave():
    record = OUT / "result.json"
    if not record.is_file():
        raise RuntimeError("02 Simulate를 먼저 실행하세요.")
    result = json.loads(record.read_text(encoding="utf-8"))
    wave = OUT / "wave.vcd"
    if result["status"] != "SIMULATED" or not wave.is_file():
        raise RuntimeError("최근 시뮬레이션이 완료되지 않았습니다. 오류를 수정하고 다시 실행하세요.")
    if result["inputs_sha256"] != inputs()[2] or result["wave_sha256"] != digest(wave):
        raise RuntimeError("소스·설정·파형이 변경되었습니다. 저장 후 02 Simulate를 다시 실행하세요.")
    return wave


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "simulate", "wave"])
    parser.add_argument("--timeout", type=int, default=120, help="컴파일·실행 각각의 제한 시간(초)")
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout은 양수여야 합니다.")
    if args.action == "check":
        check()
    elif args.action == "simulate":
        simulate(args.timeout)
    else:
        wave = current_wave()
        subprocess.run([tool("code"), "--reuse-window", str(wave)], check=True)
        print("텍스트로 열리면 탭 우클릭 → Reopen Editor With... → VaporView를 선택하세요.")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
