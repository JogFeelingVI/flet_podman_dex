# 进阶建议：一站式清理与优化
## 如果你想在清理未使用 import 的同时，还顺便对 import 进行排序（类似 isort 的功能），可以运行：
```bash
uvx ruff check --select I,F401 --fix
```