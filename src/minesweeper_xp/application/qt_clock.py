"""Qt 环境下的计时实现。

基于 QTimer 驱动 elapsed 递增，接入 Core 的 Clock 接口，
供 UI 层在应用中使用（实现见 docs/实施文档.md §13）。
"""
