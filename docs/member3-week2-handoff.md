# 三号第二周固定版本验证材料

2026-10-11 收尾状态：三号代码、测试、兼容性说明和 PR 已准备；用户反馈现有虚拟机无法执行测试，继续完成无需鸿蒙 PC 的工作。未取得该虚拟机的失败日志，原因尚未定位。
目前没有可执行本轮原生验证的鸿蒙 PC 环境，原生复测、原生工具链条件和成员交叉验证仍待执行。

## 已完成、可直接审阅

- [第二周六项要求与已有兼容修改映射](core-compatibility-week2.md)。
- [本机回归与公开证据](evidence/core-compatibility/2026-10-11/README.md)：24 核心、30 定向、17 报告测试，4 个 CLI，8 个同次受检产物一致。
- [PR #9](https://github.com/litex-harmonyos/litex-harmonyos-pc/pull/9)：源码提交 `a4929180c36004a272a2da2ed7dcec704cc24cc3`。
- [四组 Ubuntu CI](https://github.com/litex-harmonyos/litex-harmonyos-pc/actions/runs/38105516202) 均成功；新验证器的全部 5 项测试在分组日志中明确通过。CI 使用 Python 3.9，不是与鸿蒙 Python 版本对齐的端到端比较，也不是成员签字。
- CI 实际检出 PR 合并测试提交 `d2ac98407fa72264d001ad74f95d4ffd028169e3`；来源与结果见 [ci-summary.json](evidence/core-compatibility/2026-10-11/ci-summary.json) 和 [日志摘录](evidence/core-compatibility/2026-10-11/ci-excerpts.log.txt)。

## 固定版本材料包

本机 `build/member3-week2-handoff-20261011.zip` 包含完整历史的 LiteX/Migen Git bundle、依赖约束、本说明和每项 SHA-256。
LiteX 固定为上述源码提交，Migen 固定为 `4c2ae8dfeea37f235b52acb8166f12acaaae4f7c`；后续说明提交不改变这份已测试源码材料。
包的来源、摘要和本机恢复检查见 [handoff-manifest.json](evidence/core-compatibility/2026-10-11/handoff-manifest.json)。两份 bundle 已验证且从空目录实际恢复，提交及 9 个测试源码哈希均核对一致。
源码传入无需重新联网克隆；安装公共 Python 依赖仍需 PyPI 网络，本包没有包含完整离线 wheel 仓库，也没有鸿蒙 Python、编译器或工具链。

## 取得原生设备后执行

先记录实际设备型号、系统/架构、原生终端与 Python 路径；使用普通可写目录，不使用旧 venv 或旧结果目录。
将材料包解压到一个全新目录，在该目录先核对包内文件哈希：

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
manifest = json.loads(Path('package-sha256.json').read_text(encoding='utf-8'))
for name, expected in manifest.items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
print('package hashes OK')
PY
```

然后逐项执行，任一步失败保留完整输出并停止后续安装：

```sh
git clone --no-checkout litex.bundle litex
git -C litex checkout a4929180c36004a272a2da2ed7dcec704cc24cc3
git clone --no-checkout migen.bundle migen
git -C migen checkout 4c2ae8dfeea37f235b52acb8166f12acaaae4f7c
git -C litex rev-parse HEAD
git -C migen rev-parse HEAD

PIP_CONSTRAINT="$PWD/constraints.txt" \
LITEX_MIGEN_URL="$PWD/migen.bundle" \
PYTHONUTF8=1 sh litex/scripts/setup_harmonyos.sh > setup-native.log 2>&1
echo "安装退出码：$?"
```

退出码为 0，且安装日志导入成功后，执行三号入口：

```sh
cd litex
PYTHONUTF8=1 .venv-litex/bin/python scripts/run_core_compatibility.py \
  --scope native --operator '填写实际操作者' \
  --output-dir ../results/member3-week2-native --step-timeout 900
```

回收完整 results 目录、setup-native.log、litex/logs、设备与终端截图。失败时保留首次结果，重跑使用新目录。
工具链探测只是条件检查；固件需要另行实际构建，以 ELF/bin 和日志为准。仅在原生条件具备时执行 [第二周记录](core-compatibility-week2.md) 中的固件方案。
虚拟机若以后可以运行，则使用 supplementary 范围并标明虚拟机来源，不能把结果写成真机验证；不要修改平台标记绕过 native 防护。

## 合并前仍需完成

1. 三号原生导入、CLI、最小生成及回归会话，保留实际设备与原始证据。
2. 原生固件条件探测；具备条件时编译，缺项时给出条件性未运行记录。
3. 另一成员交叉验证代码、脚本和证据；组长确认跨平台差异口径并审核合并。

现有虚拟机的失败原因不能凭本机测试推断；取得日志后再定位。历史跨平台差异和最新组长 18 份原始文件尚未取得的边界继续保留。
