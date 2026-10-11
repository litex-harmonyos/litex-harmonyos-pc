# 三号 2026-10-11 首次原生会话与权限诊断

用户提供的鸿蒙 PC 原生终端会话；LiteX 固定 a4929180c，Migen 安装源码 136 个文件与固定提交一致。
原 ZIP、诊断原文件完整保存在本机，公开资料仅含测试结论、权限现象和文件校验摘要；设备、进程及路径明细不发布。原始/公开哈希和文件核查数量见 summary.json。

核心验收 5/5、24 核心、30 定向、4 CLI、最小 SoC 及同次 8 个产物比较通过。这是同一主机两入口比较，不是跨平台严格比较。
首次总报告 **FAIL**：历史权限测试假定 chmod(0500) 会拒绝写入，实际两个采样目录仍报告 02771，普通 Python 与 Builder 都能写入。诊断证明测试前提未建立，不能由此归因于 Builder 绕过权限。未据此次观察断言鸿蒙所有文件系统的行为。

## 验证器修正

历史 9 月 30 日脚本与首次报告保持原样。当前 scripts/probe_core_host.py 先以普通 Python 对同一目录中的新文件验证拒绝写入，再检查 Builder：

- 两者均 PermissionError：PASS，exercised=true。
- 两者均可写：BLOCKED，exercised=false，记录 chmod 前后状态。
- 两者行为不一致或其他错误：FAIL。

核心执行器保留 acceptance_complete 与 host_probe_complete 的区别；BLOCKED 返回 2，不能记为 PASS 或 peer-review-pending；其他必需步骤失败优先记 FAIL。
新增 7 项保护性测试，总计 26 项报告/比较测试在 Mac 通过；本机更新后补充验收 PASS。模拟的单元测试不是真机权限证据。尚待用户在原设备复跑新版流程。

真机具备 make/ninja，缺 Meson、RISC-V GCC 和三个数据包，固件为 CONDITIONS_MISSING，未编译；条件性任务没有升级成移植工具链。
原生报告测试、更新后的宿主检查、另一成员交叉验证及组长审核仍待完成。
