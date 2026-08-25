"""程序入口模块。

支持通过 ``python -m minesweeper_xp`` 启动应用：将包内的 main 函数
暴露给 Python 的 -m 机制，实际启动逻辑见 main.py 的 main()。
"""

from minesweeper_xp.main import main

if __name__ == "__main__":
    main()
