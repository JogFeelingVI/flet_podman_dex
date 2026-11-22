# @File    : config.py
# @Time    : 2026/11/20 10:46:23
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 配置文件


def configcol(**kwargs):
    """
    *宽度限定设定 配合`ResponsiveRow`使用*
    - xs	<  576px	手机竖屏
    - sm	>= 576px	手机横屏 / 小平板
    - md	>= 768px	平板电脑
    - lg	>= 992px	小型桌面显示器 / 笔记本
    - xl	>= 1200px	普通桌面显示器
    - xxl	>= 1400px	大尺寸宽屏显示器
    """
    kwargs.setdefault("xs", 12)
    return kwargs
