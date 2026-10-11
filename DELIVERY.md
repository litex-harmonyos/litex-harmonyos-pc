# LiteX 鸿蒙 PC 移植交付说明

交付状态：**核心范围完成，可以提交**  
状态确认日期：2026-10-11

## 1. 交付坐标

| 项目 | 内容 |
| --- | --- |
| 项目仓库 | <https://github.com/litex-harmonyos/litex-harmonyos-pc> |
| 最终集成分支 | `port/harmonyos-pc` |
| 已验证技术基线 | `b2ef07da0da7cd24519a027a0af7ad9318ea9366` |
| 版本标签 | `harmonyos-pc-v1.0` |
| 基线 CI | [GitHub Actions 38136675232](https://github.com/litex-harmonyos/litex-harmonyos-pc/actions/runs/38136675232)，4/4 jobs 通过 |
| LiteX 版本 | 2026.4 |
| 固定 Migen 提交 | `4c2ae8dfeea37f235b52acb8166f12acaaae4f7c` |
| 鸿蒙测试环境 | HarmonyOS / HongMeng Kernel 1.12.0，aarch64，HarmonyBrew Python 3.12.14 |

`b2ef07da0` 是完成全部功能集成、真机证据复核并通过四分片 CI 的技术基线。
`harmonyos-pc-v1.0` 指向包含本交付说明的最终收尾提交；两者之间仅允许交付文档变更。

## 2. 验收结论

| 验收项 | 结果 | 证据 |
| --- | --- | --- |
| 原生 CPython、pip 与环境探测 | PASS | [环境搭建说明](docs/harmonyos-environment-setup.md) |
| LiteX、Migen 安装与导入 | PASS | [复现说明](docs/harmonyos-pc.md) |
| LiteX CLI 基本入口 | PASS | [验证报告](PORTING_REPORT.md) |
| 便携核心测试 | PASS，24/24 | [组长真机摘要](docs/evidence/2026-10-10/lead-week2-harmonyos.json) |
| 最小 SoC 生成 | PASS | [组长真机摘要](docs/evidence/2026-10-10/lead-week2-harmonyos.json) |
| Verilog、CSR 与软件头文件 | PASS，9 个记录产物 | [验证报告](PORTING_REPORT.md) |
| 空目录安装和重复生成 | PASS | [组长参考摘要](docs/evidence/2026-10-10/lead-week2-reference.json) |
| Windows 与鸿蒙结果比较 | PASS，差异已解释并接受 | [比较报告](docs/evidence/2026-10-08/comparison.json) |
| 最终集成 CI | PASS，4/4 jobs | [Actions 运行](https://github.com/litex-harmonyos/litex-harmonyos-pc/actions/runs/38136675232) |

组长接受以下比较例外：生成文件中的提交号页眉不同，以及 Verilog 层级树注释在
Windows 和鸿蒙环境分别使用 ASCII、Unicode 连接符。CSR 结构、内存初始化内容、HDL
逻辑及软件常量没有发现行为差异。

## 3. 团队交付闭环

| 成员 | 交付内容 | 合并记录 | 状态 |
| --- | --- | --- | --- |
| 1 号（组长） | 基线、最小 SoC、验收入口、最终真机回放与集成 | PR #2、#8 | 完成 |
| 2 号 | 鸿蒙环境、安装脚本、依赖矩阵与 Migen 核查 | PR #1、#6 | 完成 |
| 3 号 | 核心兼容性核查、回归与补充真机证据 | PR #4、#9 | 完成 |
| 4 号 | 两端测试、产物比较、报告和完整证据包 | PR #3、#5 | 完成 |

仓库未启用 GitHub Issues。组长在收尾时正式确认，以功能分支、`PROJECT_PLAN.md` 中的
责任表和 PR #1 至 #9 作为四项工作的负责人及审阅记录；不再把“必须建立四个 Issue”
作为交付阻塞项。全部远端功能分支均已合入 `port/harmonyos-pc`，交付时不以个人功能
分支作为版本来源。

## 4. 交付内容索引

- [鸿蒙 PC 安装、使用与复现](docs/harmonyos-pc.md)
- [环境搭建说明](docs/harmonyos-environment-setup.md)
- [依赖兼容矩阵](docs/dependency-matrix.md)
- [核心兼容性核查](docs/core-compatibility.md)
- [完整验证报告](PORTING_REPORT.md)
- [五分钟演示流程](docs/week1-demo.md)
- [原生测试证据](docs/evidence/)
- [2026-10-08 完整证据包](docs/evidence/2026-10-08/full-evidence.zip)
- [项目计划与分工闭环](PROJECT_PLAN.md)

## 5. 已知限制

以下内容属于已声明的工具链或硬件扩展，不影响本次 Python 核心与导出范围的通过结论：

- `litex_sim` 的可选入口缺少 LiteEth；
- 鸿蒙 PC 上未完成 Verilator 全流程仿真；
- 未完成 RISC-V GCC、BIOS 或固件编译；
- 未执行 FPGA 综合、下载和板级启动；
- 权限拒绝写入用例受原生测试环境权限模型限制，按环境限制记录，不计为通过。

这些项目只有在后续明确提供对应生态依赖、工具链或 FPGA 硬件后，才进入新的扩展验收。

## 6. 提交方式

课程或项目验收提交以下信息即可：

1. 仓库地址和 `port/harmonyos-pc` 分支；
2. `harmonyos-pc-v1.0` 标签；
3. 本交付说明、验证报告和完整证据包；
4. 按 [五分钟演示流程](docs/week1-demo.md) 展示原生环境、核心测试和最小 SoC 产物。

若交付目标是 OpenHarmonyPCDeveloper 社区，还需按其 Python 三方库贡献规范，在
`Python_Package_For_HarmonyOS` 仓库单独提交来源、校验、环境、测试与限制说明。该社区
PR 是发布流程，不改变本仓库核心移植已经完成的结论。
