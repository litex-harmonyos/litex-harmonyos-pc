# 三号 2026-10-11 原生 r2 复测摘要

本次复测绑定 LiteX 提交 `2cd7d5eb43b73eab0fce3ea751e78e6d36494601`，沿用首次原生会话的固定依赖环境。三号成员回收并核验完整 r2 包；原始设备、进程和路径明细继续仅在本地保管，本目录只提交脱敏结论和归档哈希。

## 结果

- 必达验收 5/5，其中便携核心测试 24/24。
- 定向兼容回归 30/30，4 个 CLI 帮助入口成功。
- 最小 SoC 生成成功，同次 8 个受检产物 MATCH；这不是跨平台严格 MATCH。
- 报告、宿主和比较保护性测试 26/26 通过；测试内故意模拟的失败和超时属于断言输入。
- 修正后的执行器返回 `BLOCKED`、退出码 2：`acceptance_complete=true`，`host_probe_complete=false`。
- `chmod(0500)` 后目录仍报告 02771，普通 Python 与 Builder 均可写；拒绝写入前提未建立，`exercised=false`，不能把权限传播记为 PASS。
- 固件条件仍缺 Meson、RISC-V GCC、picolibc、compiler_rt 和 PicoRV32 数据包，状态为 `CONDITIONS_MISSING`、`compiled=false`。

原始 r2 ZIP 的 SHA-256 为 `3490f765d18cfbb27994dbbd9a4908c538b4660366ff98be41df12418dcaa14a`。成员记录显示 ZIP CRC、96 个回传文件哈希、42 个执行器文件哈希及 4 个更新源码哈希均已核验；审阅者未取得该原始 ZIP，因此这里只确认提交内摘要、脚本行为和公开哈希，不声称独立逐字节复核原始包。

## 独立交叉复核

组长审核在 Windows、CPython 3.12.10 上对同一提交执行：

```text
python -m unittest -v test.test_probe_core_host test.test_run_core_compatibility test.test_run_acceptance test.test_compare_baseline
Ran 26 tests
OK
```

最新提交的四组 Ubuntu CI 也全部通过。Windows 与 CI 复核验证报告逻辑和保护分支，不替代鸿蒙原生运行，也不解除权限前提 BLOCKED 或固件条件缺失。
