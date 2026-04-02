# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-04 02:53:12
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-24 07:00:52

import itertools
import re
import secrets
from collections import OrderedDict
from functools import lru_cache
from typing import List, TypedDict, Set, Tuple


# region LotteryData
class LotteryData(TypedDict, total=False):
    # total=False 表示这些键不是每一个都必须同时出现
    PA: List[int]
    PB: List[int]
    PC: List[int]
    PD: List[int]
    PE: List[int]
    PF: List[int]
    PG: List[int]
    PH: List[int]
    PI: List[int]
    PJ: List[int]


# endregion


# region randomData
class randomData:
    """根据设置随机选择数据"""

    name = "randomData"

    def __init__(self, seting):
        if not isinstance(seting, dict):
            raise ValueError("Setting must be a dictionary.")
        self.setting = seting
        # 自动发现配置中的 keys，而不是硬编码 ("pa", "pb", "pc")
        # 过滤掉非字典项（比如 "note" 字段）
        self.targets = [k for k, v in seting.items() if isinstance(v, dict)]

    def select(self, seting):
        if seting is None and not isinstance(seting, dict):
            return None
        pmin = seting.get("range_start", 0)
        pmax = seting.get("range_end", 100)
        plen = seting.get("count", 6)  # 默认选择6个数字
        if plen > pmax - pmin + 1:
            return None
        return sorted(secrets.SystemRandom().sample(range(pmin, pmax + 1), plen))

    def get_pabc(self) -> LotteryData:
        """
        {"PA":[01,02,03,04,05,06], "PB":[16]}
        :return: 返回随机数据
        """
        result = {}
        for key in self.targets:
            # 获取对应 key 的配置
            item_config = self.setting.get(key)
            # 生成数据
            numbers = self.select(item_config)

            if numbers is not None:
                result[key] = numbers

        return result

    def get_exp(self, abc: dict = None) -> str:
        """获取格式化的随机数据字符串表示"""
        if abc is None:
            pabc = self.get_pabc()
            # print(f'{pabc=}')
        else:
            pabc = abc
        parts = []
        for key in self.targets:
            item_config = self.setting.get(key)
            numbers = pabc.get(key)

            width = max(len(f"{item_config['range_end']}"), 1)
            numbers_str = [f"{x:0{width}}" for x in numbers]
            # print(f'{numbers=} {numbers_str=}')
            parts.append(" ".join(numbers_str))
        groups = OrderedDict()
        for p in parts:
            i = len(p)
            groups.setdefault(i, []).append(p)
        result_lists = list(groups.values())
        # print(f'{result_lists=}')
        match len(result_lists):
            case 1:
                return " ".join(result_lists[0])
            case 2:
                part_1 = " ".join(result_lists[0])
                part_2 = " ".join(result_lists[1])
                return f"{part_1} + {part_2}"
            case _:
                return " ".join([" ".join(g) for g in result_lists])

    @staticmethod
    def generate_secure_string(length=8):
        # 定义候选字符集：大写字母 + 小写字母 + 数字
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

        # 使用 SystemRandom 生成指定长度的随机字符串
        # secrets.choice 比 random.choice 更安全，适合生成密码或令牌
        secure_str = "".join(secrets.choice(alphabet) for _ in range(length))

        return secure_str


# endregion


# region CalcUtils
class CalcUtils:
    _primes_cache: Set[int] = set()
    _primes_max: int = 0

    @staticmethod
    def get_primes(n: int) -> Set[int]:
        """获取小于等于 n 的质数集合（包含1，兼容原逻辑）"""
        if n <= CalcUtils._primes_max:
            return CalcUtils._primes_cache

        # 埃氏筛法
        is_prime = [True] * (n + 1)
        is_prime[0] = is_prime[1] = False
        for p in range(2, int(n**0.5) + 1):
            if is_prime[p]:
                for i in range(p * p, n + 1, p):
                    is_prime[i] = False

        primes = {i for i, val in enumerate(is_prime) if val}
        primes.add(1)  # 依照原代码逻辑，将 1 视为质数处理

        # 更新缓存
        CalcUtils._primes_cache = primes
        CalcUtils._primes_max = n
        return primes

    @lru_cache(maxsize=128)
    @staticmethod
    def nwped(numbers_str: str, max_limit: int = 1000) -> Set[int]:
        """
        数字解析引擎
        :param numbers_str: 输入字符串，如 "range 1,34 --j"
        :param max_limit: 遇到 '>' 等操作符时的默认最大上限
        :return: 解析后的数字集合 (Set)
        """
        if not numbers_str or not isinstance(numbers_str, str):
            return set()

        # 1. 预处理：分离 基础定义 和 Flag (以 -- 为界)
        parts = numbers_str.split("--", 1)
        base_part = parts[0].strip().lower()
        flag_str = parts[1].strip().lower() if len(parts) > 1 else ""

        results = []

        # 2. 解析基础数字定义
        try:
            if base_part.startswith("range"):
                # 处理 "range 12,56"
                nums = [int(x) for x in re.findall(r"\d+", base_part)]
                if len(nums) >= 2:
                    results = list(range(nums[0], nums[1]))  # 不包含 nums[1]

            elif base_part.startswith("<"):
                # 处理 "<45" -> 0 到 45
                val = int(re.search(r"\d+", base_part).group())
                results = list(range(0, val + 1))

            elif base_part.startswith(">"):
                # 处理 ">12" -> 13 到 max_limit
                val = int(re.search(r"\d+", base_part).group())
                results = list(range(val + 1, max_limit + 1))

            else:
                # 处理 "12,13,15" 或 "12 13 15"
                results = [int(x) for x in re.findall(r"\d+", base_part)]
        except (ValueError, AttributeError):
            return set()

        if not results:
            return set()

        # 3. 解析并应用 Flag (Filter Logic)
        if flag_str:
            flag_type = flag_str[0]  # 'j', 'o', 'z', 'h', 'm', 'w'
            params = flag_str[1:]  # 后续数字

            if flag_type == "j":  # 奇数
                results = [x for x in results if x % 2 != 0]

            elif flag_type == "o":  # 偶数
                results = [x for x in results if x % 2 == 0]

            elif flag_type == "z":  # 质数
                primes = CalcUtils.get_primes(max(results))
                results = [x for x in results if x in primes]

            elif flag_type == "h":  # 合数 (非质数)
                primes = CalcUtils.get_primes(max(results))
                results = [x for x in results if x not in primes]

            elif flag_type == "m":  # 取模: --m312 (模3 余 1或2)
                if len(params) >= 2:
                    mod_val = int(params[0])
                    remainders = [int(x) for x in params[1:]]
                    results = [x for x in results if x % mod_val in remainders]

            elif flag_type == "w":  # 尾数: --w13 (尾数 1或3)
                if params:
                    tails = [int(x) for x in params]
                    results = [x for x in results if x % 10 in tails]

        # 最终返回 set，利用其哈希查找特性加速后续的 if x in ... 逻辑
        return set(results)

    @staticmethod
    def average(data_list: list[int]) -> int:
        if all(isinstance(x, int) for x in data_list):
            return sum(data_list) // len(data_list)
        return 0

    @staticmethod
    def xiangsidu(data_list: list[int], refer):
        if isinstance(refer, str):
            refer_set = {int(x) for x in re.findall(r"(\d+)", refer)}
        else:
            refer_set = set(refer)  # 转集合加速查找
        # print(f'debug: {refer_set}')
        # 2. 统计特征 (避免双重计数)
        cf_count = 0
        xl_count = 0

        for _d in data_list:
            # 优先判断重复
            if _d in refer_set:
                cf_count += 1
            # 如果不是重复，再判断相邻
            elif (_d + 1 in refer_set) or (_d - 1 in refer_set):
                xl_count += 1

        # 3. 计算特征指纹
        # 剩余个数
        rest_count = len(data_list) - cf_count - xl_count

        # 构造特征向量
        features = (cf_count, xl_count, rest_count)

        # 排序取最大的两个
        _a, _b = sorted(features, reverse=True)[:2]
        return _a * 10 + _b

    @staticmethod
    def lianhao(data_list: list[int]) -> int:
        lhao = [x for x in data_list if x + 1 in data_list or x - 1 in data_list]
        return len(lhao)

    @staticmethod
    def ac(data_list: list) -> int:
        """计算 N 的Ac 必须包含在【count】内部"""
        diff_set = set()
        for a, b in itertools.combinations(data_list, 2):
            diff = abs(a - b)
            diff_set.add(diff)
        return len(diff_set) - len(data_list) + 1


# endregion

# region filterFunc
_FILTER_REGISTRY = {}


def register(func):
    # 统一参数结构
    _FILTER_REGISTRY[func.__name__] = {
        "parameters": {"pabc": "LotteryData", "args": "str", "target": "str"},
        "return_type": "bool",
    }
    return func


class filterFunc:
    @staticmethod
    def getFuncName():
        # 直接返回外部生成的注册表
        return _FILTER_REGISTRY

    @register
    @staticmethod
    def avg(pabc: LotteryData, args: str, target: str) -> bool:
        if target == "all":
            avgValue = CalcUtils.average([y for x in pabc.values() for y in x])
        else:
            avgValue = CalcUtils.average(pabc[target])
        if avgValue in CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def Sum(pabc: LotteryData, args: str, target: str) -> bool:
        if target == "all":
            sumValue = sum([y for x in pabc.values() for y in x])
        else:
            sumValue = sum(pabc[target])
        if sumValue in CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def include(pabc: LotteryData, args: str, target: str) -> bool:
        targetValue = []
        if target == "all":
            targetValue = set([y for x in pabc.values() for y in x])
        else:
            targetValue = set(pabc[target])
        if targetValue & CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def not_include(pabc: LotteryData, args: str, target: str) -> bool:
        return not filterFunc.include(pabc, args, target)

    @register
    @staticmethod
    def bit(pabc: LotteryData, args: str, target: str) -> bool:
        # print(f' {args=} {target=}')
        if target == "all":
            target = list(pabc.keys())[0]
        pabctarget = pabc[target]
        if len(pabctarget) == 1:
            bitValue = pabctarget[0]
            other_part = args
        else:
            pattern = r"bit(\d+)\s+(.*)"
            match = re.search(pattern, args)
            # print(f'{match=}')
            if not match:
                return False
            idx_y = int(match.group(1))  # '2'
            other_part = match.group(2)  # '>13 --z'
            bitValue = pabc[target][idx_y - 1]

        if bitValue in CalcUtils.nwped(other_part):
            return True
        return False

    @register
    @staticmethod
    def not_bit(pabc: LotteryData, args: str, target: str) -> bool:
        return not filterFunc.bit(pabc, args, target)

    @register
    @staticmethod
    def Ac(pabc: LotteryData, args: str, target: str) -> bool:
        acValue = []
        if target == "all":
            acValue = [y for x in pabc.values() for y in x]
        else:
            acValue = pabc[target]
            if len(acValue) == 1:
                return False
        acValue = CalcUtils.ac(pabc[target])
        if acValue in CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def sum_bit_xy(pabc: LotteryData, args: str, target: str):
        """bit1,2 >13 --z"""
        # print(f'{pabc = } {args=} {target=}')
        pattern = r"bit(\d+),(\d+)\s+(.*)"
        match = re.search(pattern, args)
        # print(f'{match=}')
        if not match:
            return False

        # 2. 修正字典键的获取
        if target == "all":
            sum_bit = [y for x in pabc.values() for y in x]
        else:
            sum_bit = pabc[target]
            if len(sum_bit) == 1:
                return False
        # 3. 从分组中安全获取值
        idx_x = int(match.group(1))  # '1'
        idx_y = int(match.group(2))  # '2'
        other_part = match.group(3)  # '>13 --z'
        bitx = sum_bit[idx_x - 1]
        bity = sum_bit[idx_y - 1]
        if (bitx + bity) in CalcUtils.nwped(other_part):
            return True
        return False

    @register
    @staticmethod
    def diff_bit_xy(pabc: LotteryData, args: str, target: str):
        """bit1,2 >13 --z"""
        pattern = r"bit(\d+),(\d+)\s+(.*)"
        match = re.search(pattern, args)  # 使用 search 更方便拿分组

        if not match:
            return False

        # 2. 修正字典键的获取
        if target == "all":
            diff_bit = [y for x in pabc.values() for y in x]
        else:
            diff_bit = pabc[target]
            if len(diff_bit) == 1:
                return False

        # 3. 从分组中安全获取值
        idx_x = int(match.group(1))  # '1'
        idx_y = int(match.group(2))  # '2'
        other_part = match.group(3)  # '>13 --z'

        # 4. 获取具体号码（注意索引要 -1）
        val_x = diff_bit[idx_x - 1]
        val_y = diff_bit[idx_y - 1]

        if abs(val_x - val_y) in CalcUtils.nwped(other_part):
            return True
        return False

    @register
    @staticmethod
    def mod_x(pabc: LotteryData, args: str, target: str):
        """mod2 >13 --z"""
        pattern = r"mod(\d+)\s+(.*)"
        match = re.search(pattern, args)

        if target == "all":
            mod_list = [y for x in pabc.values() for y in x]
        else:
            mod_list = pabc[target]
        # 3. 从分组中安全获取值
        idx_x = int(match.group(1))
        other_part = match.group(2)

        modx_sum = sum([x % idx_x for x in mod_list])
        if modx_sum in CalcUtils.nwped(other_part):
            return True
        return False

    @register
    @staticmethod
    def any(pabc: LotteryData, args: str, target: str):
        if target == "all":
            # 将 keys 转为 list 后再取第一个
            pabcvalue = [y for x in pabc.values() for y in x]
        else:
            pabcvalue = pabc[target]
        if set(pabcvalue) & CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def not_any(pabc: LotteryData, args: str, target: str):
        if not filterFunc.any(pabc, args, target):
            return True
        return False

    @register
    @staticmethod
    def jiSum(pabc: LotteryData, args: str, target: str):
        if target == "all":
            jishu = [y for x in pabc.values() for y in x]
        else:
            jishu = pabc[target]
        jiList = [x for x in jishu if x % 2 == 1]
        if sum(jiList) in CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def ouSum(pabc: LotteryData, args: str, target: str):
        if target == "all":
            oushu = [y for x in pabc.values() for y in x]
        else:
            oushu = pabc[target]
        ouList = [x for x in oushu if x % 2 == 0]
        if sum(ouList) in CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def zsSum(pabc: LotteryData, args: str, target: str):
        if target == "all":
            zhishu = [y for x in pabc.values() for y in x]
        else:
            zhishu = pabc[target]
        zs = CalcUtils.get_primes(max(zhishu))
        zsList = [x for x in zhishu if x in zs]
        if sum(zsList) in CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def hsSum(pabc: LotteryData, args: str, target: str):
        if target == "all":
            heshu = [y for x in pabc.values() for y in x]
        else:
            heshu = pabc[target]
        zs = CalcUtils.get_primes(max(heshu))
        hsList = [x for x in heshu if x not in zs]
        if sum(hsList) in CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def max(pabc: LotteryData, args: str, target: str):
        if target == "all":
            maxVale = [y for x in pabc.values() for y in x]
        else:
            maxVale = pabc[target]
        if max(maxVale) in CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def min(pabc: LotteryData, args: str, target: str):
        if target == "all":
            minVale = [y for x in pabc.values() for y in x]
        else:
            minVale = pabc[target]
        # minVale = min(minVale)
        # Number_for_args = CalcUtils.nwped(args)
        if min(minVale) in CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def lianhao(pabc: LotteryData, args: str, target: str):
        if target == "all":
            targetv = [y for x in pabc.values() for y in x]
        else:
            targetv = pabc[target]
        _lh = CalcUtils.lianhao(targetv)
        # Number_for_args = CalcUtils.nwped(args)
        if _lh in CalcUtils.nwped(args):
            return True
        return False

    @register
    @staticmethod
    def xiangsidu(pabc: LotteryData, args: str, target: str):
        if target == "all":
            targetv = [y for x in pabc.values() for y in x]
        else:
            targetv = pabc[target]
        cankao, notin = args.split(" ")
        xsdu = CalcUtils.xiangsidu(targetv, cankao)
        if xsdu not in CalcUtils.nwped(notin):
            return True
        return False


# endregion


# region filter_for_pabc
class filter_for_pabc:
    METADATA = filterFunc.getFuncName()

    def __init__(self, filters: list):
        self.filters = filters
        # 预先找到函数对象，避免在 handle 循环中使用 getattr
        self.active_filters = []
        for item in filters:
            fname = item["func"]
            func_obj = getattr(filterFunc, fname, None)
            if func_obj:
                self.active_filters.append(
                    {
                        "func": func_obj,
                        "target": item.get("target", ""),
                        "condition": item.get("condition", ""),
                        # 🔴 这里是核心优化：在初始化时就把 condition 字符串解析好！
                        "parsed_condition": item.get("condition", ""),
                    }
                )

    def handle(self, pabc: dict):
        for f_info in self.active_filters:
            # 这里的调用不再需要解析字符串，不再需要反射，速度提升极快
            if not f_info["func"](pabc, f_info["parsed_condition"], f_info["target"]):
                return False
        return True


# endregion


# region calculate_lottery
def calculate_lottery(settings: dict, filters: dict = None) -> Tuple[str, bool]:
    """
    纯函数，用于单次彩票计算
    直接通过参数获取 settings 和 filters
    """
    if not settings:
        return ("No settings", False)

    # 实例化并获取数据
    rd = randomData(seting=settings["randomData"])
    result = rd.get_pabc()

    # 如果没有过滤器，直接返回 True
    if not filters:
        return (rd.get_exp(result), True)

    # 过滤校验
    filter_jp = filter_for_pabc(filters=filters)
    if not filter_jp.handle(result):
        return (rd.get_exp(result), False)

    return (rd.get_exp(result), True)


def initialization(
    settings: dict = None, filters: dict = None
) -> Tuple[randomData, filter_for_pabc]:
    """
    初始化 rd 和 ffp

    Args:
        settings (dict, optional): _description_. Defaults to None.
        filters (dict, optional): _description_. Defaults to None.

    Returns:
        Tuple[randomData, filter_for_pabc]: _description_
    """
    rd = None
    ffp = None
    if settings:
        rd = randomData(seting=settings["randomData"])
    if filters:
        ffp = filter_for_pabc(filters=filters)
    return (rd, ffp)


def calculate_lottery_rdffp(
    rd: randomData, ffp: filter_for_pabc = None, status: str = "calculating"
) -> Tuple[str, bool] | str:
    """全新的数据构建器"""
    if not isinstance(rd, randomData):
        return "rd Parameter error"
    result = rd.get_pabc()
    if not ffp:
        return (rd.get_exp(result), True)

    if not ffp.handle(result):
        return (rd.get_exp(result), False)

    return (rd.get_exp(result), True)


def calculate_batch_wrapper(settings: dict, filters: dict, chunk_size=100):
    """
    【安卓优化核心】：任务打包封装
    在一次线程调度中执行多次计算，减少线程切换开销
    """
    if not settings:
        return []

    # --- 1. 预初始化 (只做一次) ---
    # 初始化生成器
    rd = randomData(seting=settings["randomData"])
    # 初始化过滤引擎 (这里会完成函数绑定和元数据准备)
    engine = filter_for_pabc(filters=filters) if filters else None
    valid_results = []
    # --- 2. 高速循环 ---
    for _ in range(chunk_size):
        # 产生原始数据 (dict)
        result = rd.get_pabc()
        # 校验逻辑
        if engine:
            if not engine.handle(result):
                continue  # 没过过滤，直接下一注，不浪费 CPU 做字符串转换
        # --- 3. 延迟转换 (Lazy Formatting) ---
        # 只有真正中奖/需要的号码，才调用 get_exp 转换成字符串
        # 这一步很费时间，跳过没用的号码能提升一倍以上的速度
        formatted_res = rd.get_exp(result)
        valid_results.append(formatted_res)
        # 如果你只需要 1 注，可以在这里直接 break
        # if len(valid_results) >= 1: break
    return valid_results


# endregion
