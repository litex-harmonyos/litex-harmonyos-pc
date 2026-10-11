# 三号第二周核心兼容性记录

日期：2026-10-11。工作分支：feature/core-compatibility；集成输入：`ea85022cfcc26fcd322d4548f95e4e103b148aa3`。
Migen 固定为 `4c2ae8dfeea37f235b52acb8166f12acaaae4f7c`，不能用同版本号的 PyPI 包替代。

## 当前结论与未完成项

本轮完成已有兼容修改复核、本机 CPython 3.12.10 旁证、一次性验证入口及证据整理；没有发现需要新增 LiteX 核心补丁的失败。
**三号第二周尚未全部完成：目前没有可用鸿蒙 PC，原生复测、当前真机工具链探测及组员交叉验证仍待执行。**
初次 HDC 查询为空；用户随后提供的虚拟机无法执行测试，已明确先完成不需鸿蒙 PC 的部分。未取得虚拟机失败日志，原因未定位。目前没有可执行本轮原生验证的环境。本机结果限定为 macOS 旁证，不作为分工要求的 Windows/Linux 参考运行或鸿蒙真机运行。

## 对应六项任务

| 三号第二周要求 | 本轮完成内容 | 状态 |
| --- | --- | --- |
| 在鸿蒙 PC 导入与显示 CLI 帮助 | 已核对一号/四号原生记录；本机 4 个帮助入口成功；原生执行入口已准备 | 三号原生会话待执行 |
| 最小 SoC 及 Verilog/CSR/头文件 | 本机直接运行鸿蒙示例入口；与基准 8 个文件比较 MATCH | 本机通过；三号原生入口待执行 |
| 工具链可用时 BIOS/最小固件 | 收集本机工具/包可见性；核对原生已提交的条件不足记录 | 条件性未运行；真机新探测待执行 |
| 按四号回归修复差异和错误 | 复核已合入接口修复和路径断言；去重后的 30 项定向回归通过 | 本轮无新增核心修复依据 |
| 每个兼容修改的测试、注释与说明 | 下表给出已有修改、用途、提交及测试；新增验证器有 5 项保护性测试 | 本机完成 |
| PR 提交集成分支 | 本轮代码、说明及脱敏证据向 port/harmonyos-pc 提交草稿 PR | 原生/交叉验证后再审核合并 |

## 已合入修改的复核

| 修改 | 来源与用途 | 回归覆盖 |
| --- | --- | --- |
| 路径登记断言比较 realpath | 三号第一周 c71e95d6a；/var 与 /private/var 路径别名导致误报；未改工具链产物 | GenericToolchain 的生成/登记与 cwd 恢复测试 |
| stream.byte_count | 5671a1896；兼容 LiteEth 对有效字节数量的接口要求 | test.interconnect.test_stream.TestStream.test_byte_count，含 1/2/4/8 位全部输入 |
| stream.byte_mask | df287c192；恢复按有效字节数量生成掩码的生态接口 | test_byte_mask，含 1/2/4/8 位、0 至 width 的计数 |
| Pmod 兼容辅助资源 | ed0c556c3；GPIO、UART、双 USB 资源描述供板卡生态使用 | test.build.test_pmod.TestPmod 的 3 项引脚/布局测试 |
| 外部仓库固定版本 | PR #7；litex-boards 与 VexRiscv SMP 数据仓库稳定集成 CI | 既有 36 项安装器测试及已成功的集成 CI，本次不重复宣称执行 |
| 验收脚本的失败/超时保留日志 | PR #8；命令异常仍输出报告 | 本轮复跑 test.test_run_acceptance 的 4 项测试 |

这些已有生态修复不是鸿蒙专属补丁，当前集成版本不能笼统写成“核心源码从未修改”。
本轮没有修改 `litex/`；新增的是三号验证入口与报告测试。

## 本轮实际执行

- 主机：macOS 26.5.2 arm64；CPython 3.12.10（独立 uv 运行时/venv）。
- 公共依赖采用四号 10 月 8 日证据中的固定约束，加入 Migen 的 Colorama 0.4.6。
- 从官方 M-Labs Git 仓库检出固定 SHA1 后构建安装 Migen；安装后的 136 个 Python 文件与固定源码逐字节相同。
- LiteX 从三号工作树可编辑安装，测试输入是 ea85022cf 加新增验证器/测试；源码哈希与原始报告保留该工作树状态。
- Mac CPython 3.12.14 无 uv 下载项，采用与既有 Windows 相同的 3.12.10 做旁证；未把它写成与鸿蒙补丁版本一致。

| 检查 | 实际结果 |
| --- | --- |
| 必达验收 | 5/5；其中便携核心 24/24 |
| client / term / soc_gen / periph_gen 帮助 | 4/4 返回 0 |
| 去重定向回归 | 30/30：原 25 项加 byte_count、byte_mask、3 项 Pmod；路径测试不重复计数 |
| VCD 临时文件/释放、中文路径编码、拒绝写入、子进程、串口枚举 | 5/5；权限项确已执行；macOS 串口枚举 3 项，未打开端口 |
| 鸿蒙示例入口 | 中文空格输出路径成功生成 9 个文件与摘要 |
| 包装入口与同次基准比较 | 8 个受检文件 MATCH（按已有时间戳/换行规则） |
| 验证器保护性测试与既有报告/比较测试 | 17/17，其中新增 5 项；拒绝伪原生范围、拒绝覆盖旧证据、拒绝 skip/空报告、拒绝未执行权限验证 |
| 可选仿真 | LiteEth 缺失，OPTIONAL_FAIL；未执行 Verilator |

实际命令、报告、原始/脱敏哈希见 [2026-10-11 证据](evidence/core-compatibility/2026-10-11/README.md)。

## 不依赖设备的收尾

[PR #9](https://github.com/litex-harmonyos/litex-harmonyos-pc/pull/9) 已提交为草稿，源码提交 `a4929180c36004a272a2da2ed7dcec704cc24cc3`。
该源码的 [四组 Ubuntu CI](https://github.com/litex-harmonyos/litex-harmonyos-pc/actions/runs/38105516202) 全部成功；实际检出的是与集成分支合并的测试提交 `d2ac98407fa72264d001ad74f95d4ffd028169e3`。

| CI 组 | pytest 主分组结果 |
| --- | --- |
| 1 | 372 passed、1 skipped；另有独立 QEMU 协同仿真步骤成功 |
| 2 | 402 passed |
| 3 | 367 passed、1 skipped |
| 4 | 382 passed、1 skipped |

新增验证器 5 项测试在组 2/3/4 的日志中明确全部通过。CI 使用 Ubuntu 22.04 和主解释器 Python 3.9，不能写成与鸿蒙 Python 版本一致的端到端比较或成员交叉验证签字。
完整下载的解码日志副本在本机持久归档；来源、摘要与公开摘录见 [ci-summary.json](evidence/core-compatibility/2026-10-11/ci-summary.json)。
上述 CI 绑定源码提交；本轮后续文档提交的 CI 状态需单独查看，不将其自动写成该次运行的一部分。

固定 LiteX/Migen 的完整 Git bundle、约束及设备恢复步骤已整理为 [验证材料](member3-week2-handoff.md)。包的哈希和空目录恢复检查已完成，代码、报告、归档和待执行步骤均可审阅。
未新增核心改动，因此没有为收尾重复运行本机核心测试。还需要成员的独立交叉验证和组长审核。

## 已有原生证据的复核边界

四号 10 月 8 日在 `ed0c556c3` 两端各通过 5/5 必达、24/24 核心、6/6 定向回归，另有 4 个 CLI、中文空格重复生成与参数/清理保护结果。
本次核对完整 ZIP 的 SHA-256、CRC 和内部 95 个文件哈希，均通过；这是档案核查，不是三号独立真机复跑。

组长 10 月 10 日在原生 `fe3261f0e` 上通过增强验收 5/5、24/24及最小生成。
ea85022cf 与 fe3261f0e 的 `litex/`、两个最小示例、核心验收和比较工具没有差异，可以作为当前核心代码的已有真机证据。
组长最新 18 份原始文件未提供到本机，本次只核对已提交摘要和哈希，不声称已取得并逐字节验证这批文件。

Windows 3.12.10 与鸿蒙 3.12.14 的差异继续保留。
原有跨平台机器比较仍为 DIFFERENT；ASCII/Unicode 层级树注释和不同提交号页眉需要独立说明，不能把本轮同主机 MATCH 写成两端严格 MATCH。
组长报告已经记载例外和核心范围处理完成，但历史摘要仍写 PENDING；最终交叉验证应引用明确的决定日期/记录，不改写历史 JSON。

## 原生一次性入口与固件条件

在已按二号流程安装固定依赖的原生环境、新专用结果目录执行：

```sh
PYTHONUTF8=1 .venv-litex/bin/python scripts/run_core_compatibility.py \
  --scope native --operator '填写实际操作者' \
  --output-dir ../results/member3-week2-native --step-timeout 900
```

入口包含完整环境探测、无 skip 核心验收、4 个 CLI、30 项回归、宿主边界检查、鸿蒙示例与同次基准比较、版本记录及固件条件探测。
它要求新的输出目录，拒绝覆盖已有结果；native 范围要求平台中有 HarmonyOS/HongMeng/OpenHarmony/ohos 标记。标记仅是误用防护，运行者仍须记录实际设备及原生会话来源。
脚本只检查工具版本和包，不会安装工具、打开串口或自动宣称固件构建成功。
本机验证模式使用 `--scope supplementary`，报告明确写 native-validation-pending。

本机缺少 Meson、Ninja、RISC-V GCC 及 picolibc/compiler_rt/PicoRV32 数据包。
已提交鸿蒙记录只说明这些扩展工具在当时未于 PATH 发现；本机缺项不代表鸿蒙当前缺项或平台不支持。
原生设备可用后，由二号确认工具/包，三号才进行实际 BIOS 编译。基准 CPU=None，不能用它证明 BIOS 构建。

若已具备对应工具链和数据包，拟采用已有 standalone generator 的最小 PicoRV32 配置：

```sh
PYTHONUTF8=1 .venv-litex/bin/python -m litex.tools.litex_soc_gen \
  --cpu-type picorv32 --cpu-variant standard --uart-name stub \
  --integrated-rom-size 65536 --integrated-sram-size 8192 \
  --no-compile-gateware --output-dir ../results/member3-week2-firmware
```

该命令当前是**待验证方案**，本轮未运行；所列参数已在本轮 soc_gen 的帮助输出中确认。执行前仍须核对 CPU/工具链条件；成功要以 BIOS ELF/bin 和完整构建日志为准，失败要保留准确阶段。
条件不满足则保留 CONDITIONS_MISSING/NOT_RUN，不把从头移植 GCC 或 Verilator 加入本轮范围。

## 收尾缺项

1. 获得鸿蒙 PC 或明确的协作执行人员，在固定输入上执行三号原生入口并回收报告、日志和产物。
2. 根据原生工具探测决定固件是否可运行，给出构建结果或条件性阻塞记录。
3. 另一成员交叉验证本轮验证器与证据；一号确认最终版本/注释差异口径，并审核合并第二周 PR。
4. 核心代码如出现新失败，只在实际复现后作最小修改并补相应测试；目前没有该类失败。
