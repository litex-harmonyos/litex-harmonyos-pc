# 三号第二周：本机旁证与原生待执行入口

2026-10-11，Codex 按三号成员授权在 macOS 26.5.2 arm64、CPython 3.12.10 上执行。
**本目录没有本轮鸿蒙真机运行；用户确认当前没有鸿蒙 PC。第二周完成状态为 native-validation-pending。**

## 输入与结果

输入是集成提交 `ea85022cfcc26fcd322d4548f95e4e103b148aa3` 加新增验证器及测试。
执行时这两个文件尚未提交；原始 report.json 保留当时工作树状态，不能把该提交号单独当作新验证器来源。
[source-sha256.json](source-sha256.json) 记录 9 个相关源码哈希，原始 ZIP 另附对应的 tested-source 文件快照。
Migen 从官方仓库固定提交 `4c2ae8dfeea37f235b52acb8166f12acaaae4f7c` 构建；136 个已安装 Python 文件与固定源码一致。
依赖约束见 [constraints.txt](constraints.txt)，实际安装项见 [packages.log.txt](logs/packages.log.txt)。

| 检查 | 结果与直接证据 |
| --- | --- |
| 无 skip 必达验收 | [5/5 报告](acceptance/acceptance-report.json)，[24 项核心测试](acceptance/logs/portable-core-tests.log.txt) |
| 去重兼容回归 | [30/30](logs/compatibility-regressions.log.txt)，选择列表见 report.json 的 command |
| CLI 帮助 | client、term、soc_gen、periph_gen 各返回 0，见 [总报告](report.json) 和 logs/ 中 4 份帮助输出 |
| 宿主边界 | [5 项通过](logs/host-probe.log.txt)；权限拒绝确已执行，串口只枚举未打开 |
| 鸿蒙示例入口与基准 | [8 个文件 MATCH](wrapper-comparison.json)，仅同次本机比较；生成文件全部保留在原始 ZIP |
| 报告保护性测试 | [17/17](reporting-tests.txt)，含新增验证器 5 项、既有验收 4 项、比较 8 项 |
| 固件 | 本机 CONDITIONS_MISSING、compiled=false；真机条件尚未新探测 |
| 可选仿真 | LiteEth 未安装，OPTIONAL_FAIL；没有实际执行 Verilator |

报告保护性测试会故意调用不存在的命令、失败命令和超时命令；日志中的这些模拟 FAIL 属于预期断言，最终 unittest 为 OK。
24 项核心、30 项定向、17 项报告测试分别记录，部分覆盖重叠，不相加宣称独立测试总数。
固件探测只检查 PATH 与 Python 数据包，不是编译成功证明。

## 原始与公开证据

本机持久归档：`<LOCAL_REPOSITORY>/build/member3-week2-20261011.zip`，未提交到 Git。
SHA-256：`8970fb668e21b0ec1eeaec87822181054654dc7d25147ff88eb32dbe94e43e46`。
ZIP 包含 58 个经哈希检查的原始文件及 archive-sha256.json：完整结果、两套最小产物、控制台/报告测试、固定约束和测试源码快照；CRC 与内部哈希检查通过。

[manifest.json](manifest.json) 分别列出公开副本哈希和对应原始条目哈希；公开副本将个人目录、工作树、venv 和临时根目录替换为占位符，保留 /private 临时路径别名区别。
公开日志采用 .log.txt 后缀，保留原有横幅尾部空格；约束副本保留原始 CRLF 换行。因此证据文件可能触发 Git 空白检查，源码和说明文件已单独通过检查。原始输出字节没有被修改，原始与脱敏副本哈希不能混用。
执行器的 file-sha256.json 按执行时点生成，未包含随后写入的 report.json、manifest 及源码审计；ZIP 内部 archive-sha256.json 则覆盖归档时全部文件（不含自身）。

## 既有真机证据及接续

[source-audit.json](source-audit.json) 记录四号 10 月 8 日完整档案的 95 项哈希核对，以及最新已原生测试版本到集成输入的核心/基准代码无差异检查。
这是既有证据的复核，不是三号独立真机验证。组长最新 18 份原始文件尚未取得，仅有仓库摘要与哈希；未声称验证其原始字节。
历史跨平台 DIFFERENT 不因本次同主机 MATCH 而消失。

设备可用后，按 [第二周记录](../../../core-compatibility-week2.md) 在固定环境执行原生入口，使用新的结果目录。
原生入口拒绝无鸿蒙平台标记的 native 范围；标记是误用防护，操作者仍需提供实际设备与原生会话来源。
随后由另一成员交叉验证，组长确认跨平台差异口径并审核 PR。
