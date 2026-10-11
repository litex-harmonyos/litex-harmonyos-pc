#!/usr/bin/env python3
"""Collect member-3 week-two checks on the explicitly selected host.

Run from an installed, pinned LiteX/Migen environment. This does not install
tools, open serial ports, or claim that a supplementary host is HarmonyOS.
"""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from run_acceptance import ROOT, git_value, run_step, utc_now


TESTS = [
    "test.build.test_generic_platform_toolchain.TestGenericToolchain",
    "test.soc.test_builder.TestBuilderPaths",
    "test.soc.test_builder.TestBuilderGeneratedFiles.test_generate_includes_without_bios_writes_runtime_headers_only",
    "test.soc.test_builder.TestBuilderGeneratedFiles.test_generate_csr_map_writes_default_csv_and_json_exports",
    "test.soc.test_builder.TestBuilderGeneratedFiles.test_variables_contents_remaps_replay_support_paths",
    "test.hdl.test_migen_compat",
    "test.interconnect.test_stream.TestStream.test_byte_count",
    "test.interconnect.test_stream.TestStream.test_byte_mask",
    "test.build.test_pmod.TestPmod",
]


def has_native_marker():
    identity = (platform.platform() + " " + platform.release()).lower()
    return any(marker in identity for marker in ("harmonyos", "hongmeng", "openharmony", "ohos"))


def acceptance_complete(report):
    """A skipped or empty acceptance report must not satisfy this checkpoint."""
    expected = {"pip-check", "imports", "litex-cli-help", "portable-core-tests", "minimal-soc"}
    passed = {step["name"] for step in report.get("steps", [])
              if step.get("required") and step.get("status") == "PASS"}
    return (report.get("status") == "PASS" and
            report.get("required_passed") == report.get("required_total") == 5 and
            expected <= passed)


def host_probe_complete(report):
    """Keep actual failures and unexercised permissions distinct from PASS."""
    expected = {"vcd_tempfile_and_cleanup", "builder_unicode_path_and_encoding",
                "builder_write_permission", "filtered_subprocess_argv_and_exit"}
    checks = {item["name"]: item for item in report.get("checks", [])}
    return (all(checks.get(name, {}).get("status") == "PASS" for name in expected) and
            checks.get("builder_write_permission", {}).get("detail", {}).get("exercised") is True)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def firmware_conditions():
    names = ("make", "meson", "ninja", "riscv64-unknown-elf-gcc",
             "riscv64-elf-gcc", "riscv32-unknown-elf-gcc")
    tools = {}
    for name in names:
        executable = shutil.which(name)
        entry = {"path": executable}
        if executable:
            try:
                result = subprocess.run([executable, "--version"], capture_output=True,
                                        text=True, encoding="utf-8", errors="replace", timeout=15)
                entry.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
            except (OSError, subprocess.TimeoutExpired) as error:
                entry["error"] = str(error)
        tools[name] = entry
    packages = {}
    for name in ("pythondata_software_picolibc", "pythondata_software_compiler_rt", "pythondata_cpu_picorv32"):
        spec = importlib.util.find_spec(name)
        packages[name] = None if spec is None else spec.origin
    missing = [name for name in ("make", "meson", "ninja")
               if tools[name].get("returncode") != 0]
    if not any(tools[name].get("returncode") == 0 for name in names[3:]):
        missing.append("RISC-V GCC")
    missing.extend(name for name, origin in packages.items() if origin is None)
    return {"status": "CONDITIONS_MISSING" if missing else "BUILD_NOT_RUN",
            "tools": tools, "packages": packages, "missing": missing,
            "compiled": False, "note": "PATH/package probe only; firmware compilation is a separate conditional task."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, help="New dedicated result directory; existing paths are refused.")
    parser.add_argument("--operator", required=True, help="Actual operator or authorized collaborating operator.")
    parser.add_argument("--scope", choices=("native", "supplementary"), required=True)
    parser.add_argument("--step-timeout", type=float, default=900)
    args = parser.parse_args()
    if args.step_timeout <= 0:
        parser.error("--step-timeout must be positive")
    output = Path(args.output_dir).resolve()
    if output.exists():
        parser.error("Use a new output directory; existing evidence must not be overwritten")
    output.mkdir(parents=True)
    report = {"started_at_utc": utc_now(), "operator": args.operator, "scope": args.scope,
              "platform": platform.platform(), "python": sys.version, "executable": sys.executable,
              "source_commit": git_value("rev-parse", "HEAD"),
              "source_status": git_value("status", "--porcelain"), "steps": []}
    if args.scope == "native" and not has_native_marker():
        report.update(status="REFUSED", reason="Native scope requested without a HarmonyOS platform marker")
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 2

    # Set reproducible text handling for subprocesses; report the controlling environment.
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    logs = output / "logs"
    logs.mkdir()
    python = sys.executable

    def run(name, command, required=True):
        result = run_step(name, command, logs, required=required, timeout=args.step_timeout)
        report["steps"].append(result)
        return result

    mode = ["--full"] if args.scope == "native" else []
    run("environment-probe", [python, str(ROOT / "scripts/check_environment.py"), *mode,
                              "--json", str(output / "environment-probe.json")])
    run("core-acceptance", [python, str(ROOT / "scripts/run_acceptance.py"),
                            "--output-dir", str(output / "acceptance"),
                            "--step-timeout", str(args.step_timeout)])
    for module in ("litex_client", "litex_term", "litex_soc_gen", "litex_periph_gen"):
        run(module + "-help", [python, "-m", "litex.tools." + module, "--help"])
    run("module-provenance", [python, "-c",
        "import json,litex,migen,litex.gen,litex.build,litex.soc; "
        "print(json.dumps({'litex':litex.__file__,'migen':migen.__file__}))"])
    run("compatibility-regressions", [python, "-m", "unittest", "-v", *TESTS])
    run("host-probe", [python, str(ROOT / "docs/evidence/core-compatibility/2026-09-30/host_probe.py")])
    run("harmonyos-example", [python, str(ROOT / "examples/harmonyos_minimal_soc.py"),
                              "--output-dir", str(output / "中文 空格"), "--clean"])
    run("wrapper-comparison", [python, str(ROOT / "scripts/compare_baseline.py"),
                                str(output / "acceptance/minimal-soc"), str(output / "中文 空格"),
                                "--output", str(output / "wrapper-comparison.json")])
    run("packages", [python, "-m", "pip", "freeze", "--all"])

    acceptance = read_json(output / "acceptance/acceptance-report.json")
    probe = read_json(logs / "host-probe.log")
    report["acceptance_complete"] = acceptance_complete(acceptance)
    report["host_probe_complete"] = host_probe_complete(probe)
    report["firmware"] = firmware_conditions()
    report["serial"] = next((item for item in probe.get("checks", [])
                             if item["name"] == "serial_enumeration_only"), {"status": "NOT_RECORDED"})
    report["native_execution"] = args.scope == "native" and has_native_marker()
    passed = all(item["status"] == "PASS" for item in report["steps"] if item["required"])
    report["status"] = "PASS" if passed and report["acceptance_complete"] and report["host_probe_complete"] else "FAIL"
    report["week2_completion"] = "peer-review-pending" if report["native_execution"] else "native-validation-pending"
    report["finished_at_utc"] = utc_now()
    files = {path.relative_to(output).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(output.rglob("*")) if path.is_file()}
    (output / "file-sha256.json").write_text(json.dumps(files, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{args.scope}: {report['status']}; completion: {report['week2_completion']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
