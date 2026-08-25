"""计时抽象（Clock）。

定义 Core 依赖的计时接口与测试用的 FakeClock，使 Core 不直接依赖
Qt 的 QTimer（实现见 docs/实施文档.md §9）。
"""
