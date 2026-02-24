# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-04 02:53:12
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-23 03:52:00


import secrets
import itertools
import re
import inspect
from typing import TypedDict, List, get_type_hints
from collections import OrderedDict


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
    def zs(max_val=18):
        """
        计算小于或等于 max_val 的所有质数，并将 1 也包含在内。

        Args:
            max_val (int): 要查找质数的上限（包含此值）。默认为 18。

        Returns:
            list: 包含 1 和所有小于或等于 max_val 的质数的列表，按升序排列。
                如果 max_val < 1 返回空列表。
        """
        # --- 输入验证和边缘情况处理 ---
        if not isinstance(max_val, int):
            return []
        if max_val < 1:
            # 因为要求包含 1，所以小于 1 的上限没有有效数字
            return []
        if max_val == 1:
            return [1]  # 特殊情况：如果上限是 1，只返回 [1]

        # --- Sieve of Eratosthenes 算法 ---
        # 1. 创建一个布尔列表 `is_prime`，长度为 max_val + 1。
        #    `is_prime[i]` 为 True 表示数字 `i` *可能*是质数。
        #    初始化所有大于等于 2 的数为 True。
        is_prime = [True] * (max_val + 1)
        is_prime[0] = is_prime[1] = False  # 0 和 1 按标准定义不是质数

        # 2. 从第一个质数 2 开始遍历
        p = 2
        # 优化：只需要检查到 sqrt(max_val)，因为如果 n 有一个大于 sqrt(n) 的因子，
        # 它必定有一个小于 sqrt(n) 的因子，这个因子在之前就会被筛掉。
        while p * p <= max_val:
            # 如果 p 是质数（即 is_prime[p] 仍为 True）
            if is_prime[p]:
                # 将 p 的所有倍数（从 p*p 开始）标记为非质数
                # 因为小于 p*p 的 p 的倍数（如 2*p, 3*p）应该已经被更小的质数筛掉了
                for i in range(p * p, max_val + 1, p):
                    is_prime[i] = False
            p += 1  # 检查下一个数

        # --- 构建结果列表 ---
        # 3. 收集结果
        primes_list = [1]  # 首先加入特殊要求的 1
        for num in range(2, max_val + 1):
            if is_prime[num]:
                primes_list.append(num)

        return primes_list

    @staticmethod
    def nwped(numbers: str):
        """
        优化后的数字处理函数
        Supported formats:
            "12,13,15"
            "range 12,56" (12 to 55)
            "<45" (0 to 44)
            ">12" (13 to 5000)
        Supported flags:
            --j (Odd), --o (Even)
            --z (Prime), --h (Composite)
            --m312 (Mod 3 rem 1 or 2) -> General format --m[mod][rem1][rem2]...
            --w13 (Ends with 1 or 3)
        """
        if not numbers:
            return []

        # 1. 预处理：分离 基础定义 和 参数Flag
        # 查找第一个 -- 的位置
        flag_match = re.search(r"(--[a-z0-9]+)", numbers)
        flag_str = ""

        if flag_match:
            # 如果有flag，截取前半部分作为数字定义，后半部分作为flag
            flag_start = numbers.find(flag_match.group(0))
            base_str = numbers[:flag_start].strip()
            flag_str = numbers[
                flag_start:
            ].strip()  # 这里假设只处理一个主flag，或者保留后续扩展
        else:
            base_str = numbers.strip()

        number_ls = []

        # 2. 解析基础数字 (Base Logic)
        # 使用完整匹配 ^...$ 避免只匹配到头部
        if base_str.startswith("range"):
            # Matches: "range 12,56"
            nums = re.findall(r"\d+", base_str)
            if len(nums) >= 2:
                number_ls = list(range(int(nums[0]), int(nums[1])))

        elif re.match(r"^[<>]", base_str):
            # Matches: ">12", "<45"
            operator = base_str[0]
            val = int(re.findall(r"\d+", base_str)[0])
            if operator == ">":
                number_ls = list(range(val, 2001))  # >12 从 13 开始
            elif operator == "<":
                number_ls = list(range(0, val + 1))  # <45 到 44 结束 (假设非负)

        elif re.match(r"^[\d,]+$", base_str):
            # Matches: "12,13,15"
            number_ls = [int(x) for x in re.findall(r"\d+", base_str)]

        else:
            # 兜底：尝试直接提取所有数字
            if not number_ls:
                number_ls = [int(x) for x in re.findall(r"\d+", base_str)]

        # 3. 解析并应用 Flag (Filter Logic)
        if flag_str:
            # 提取 flag 类型和参数
            # 兼容 --j, --o, --z, --h, --m312, --w13
            flag_type = flag_str[:3]  # --j, --m, --w
            flag_params = flag_str[3:]  # 后续的数字

            match flag_type:
                case "--j":  # 奇数
                    number_ls = [x for x in number_ls if x % 2 != 0]
                case "--o":  # 偶数
                    number_ls = [x for x in number_ls if x % 2 == 0]
                case "--z":  # 质数
                    if not number_ls:
                        return []
                    primes = CalcUtils.zs(max(number_ls) + 1)
                    number_ls = [x for x in number_ls if x in primes]
                case "--h":  # 合数 (非质数)
                    if not number_ls:
                        return []
                    primes = CalcUtils.zs(max(number_ls) + 1)
                    number_ls = [x for x in number_ls if x not in primes]
                case _ if flag_type.startswith("--m"):  # 取模 --m312 (模3 余 1,2)
                    # 这种格式其实很危险，建议 --m3,1,2，但为了兼容原逻辑：
                    # 假设第一位是除数，后面是余数列表
                    if len(flag_params) >= 2:
                        mod_val = int(flag_params[0])  # 取 '3'
                        remainders = [int(x) for x in flag_params[1:]]  # 取 ['1', '2']
                        number_ls = [x for x in number_ls if x % mod_val in remainders]
                case _ if flag_type.startswith("--w"):  # 尾数 --w13 (尾数 1,3)
                    if flag_params:
                        tails = [int(x) for x in flag_params]
                        number_ls = [x for x in number_ls if x % 10 in tails]

        return number_ls if len(number_ls) < 10 else set(number_ls)

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
class filterFunc:
    @staticmethod
    def getFuncName():
        methods_info = {}
        # 获取 filterFunc 类中的所有成员
        # 因为是静态方法，在类级别它们被视为 function
        for name, func in inspect.getmembers(filterFunc, predicate=inspect.isfunction):
            # 排除掉 getFuncName 本身和内置的 __ 方法
            if name == "getFuncName" or name.startswith("__"):
                continue

            # 获取函数签名
            sig = inspect.signature(func)

            # 解析参数
            params = {}
            for param_name, param in sig.parameters.items():
                # 获取类型注解的名称
                if param.annotation is inspect.Parameter.empty:
                    type_name = "any"
                elif hasattr(param.annotation, "__name__"):
                    type_name = param.annotation.__name__
                else:
                    # 处理像 LotteryData (TypedDict) 或 List[int] 这种复杂类型
                    type_name = str(param.annotation).replace("typing.", "")

                params[param_name] = type_name

            # 解析返回值类型
            if sig.return_annotation is inspect.Signature.empty:
                return_type = "any"
            elif hasattr(sig.return_annotation, "__name__"):
                return_type = sig.return_annotation.__name__
            else:
                return_type = str(sig.return_annotation)

            methods_info[name] = {"parameters": params, "return_type": return_type}

        return methods_info

    @staticmethod
    def avg(pabc: LotteryData, args: str, target: str) -> bool:
        if target == "all":
            avgValue = CalcUtils.average([y for x in pabc.values() for y in x])
        else:
            avgValue = CalcUtils.average(pabc[target])
        Number_for_args = CalcUtils.nwped(args)
        if avgValue in Number_for_args:
            return True
        return False

    @staticmethod
    def Sum(pabc: LotteryData, args: str, target: str) -> bool:
        if target == "all":
            sumValue = sum([y for x in pabc.values() for y in x])
        else:
            sumValue = sum(pabc[target])
        Number_for_args = CalcUtils.nwped(args)
        if sumValue in Number_for_args:
            return True
        return False

    @staticmethod
    def include(pabc: LotteryData, args: str, target: str) -> bool:
        targetValue = []
        if target == "all":
            targetValue = set([y for x in pabc.values() for y in x])
        else:
            targetValue = set(pabc[target])
        Number_for_args = set(CalcUtils.nwped(args))
        if targetValue & Number_for_args:
            return True
        return False

    @staticmethod
    def not_include(pabc: LotteryData, args: str, target: str) -> bool:
        return not filterFunc.include(pabc, args, target)

    @staticmethod
    def bit(pabc: LotteryData, args: str, target: str) -> bool:
        if target == "all":
            target = list(pabc.keys())[0]
        pabctarget = pabc[target]
        if len(pabctarget) == 1:
            bitValue = pabctarget[0]
            other_part = args
        else:
            pattern = r"bit(\d+)\s+(.*)"
            match = re.search(pattern, args)
            if not match:
                return False
            idx_y = int(match.group(1))  # '2'
            other_part = match.group(2)  # '>13 --z'
            bitValue = pabc[target][idx_y - 1]

        Number_for_args = CalcUtils.nwped(other_part)
        if bitValue in Number_for_args:
            return True
        return False

    @staticmethod
    def not_bit(pabc: LotteryData, args: str, target: str) -> bool:
        return not filterFunc.bit(pabc, args, target)

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

        Number_for_args = CalcUtils.nwped(args)
        if acValue in Number_for_args:
            return True
        return False

    @staticmethod
    def sum_bit_xy(pabc: LotteryData, args: str, target: str):
        """bit1,2 >13 --z"""
        pattern = r"bit(\d+),(\d+)\s+(.*)"
        match = re.search(pattern, args)
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
        Number_for_args = CalcUtils.nwped(other_part)
        if (bitx + bity) in Number_for_args:
            return True
        return False

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

        # 5. 计算逻辑
        diff_value = abs(val_x - val_y)

        # 假设 CalcUtils.nwped 处理字符串并返回一个列表/集合
        Number_for_args = CalcUtils.nwped(other_part)

        if diff_value in Number_for_args:
            return True
        return False

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
        Number_for_args = CalcUtils.nwped(other_part)
        if modx_sum in Number_for_args:
            return True
        return False

    @staticmethod
    def any(pabc: LotteryData, args: str, target: str):
        if target == "all":
            # 将 keys 转为 list 后再取第一个
            pabcvalue = [y for x in pabc.values() for y in x]
        else:
            pabcvalue = pabc[target]
        Number_for_args = CalcUtils.nwped(args)
        if set(pabcvalue) & set(Number_for_args):
            return True
        return False

    @staticmethod
    def not_any(pabc: LotteryData, args: str, target: str):
        if not filterFunc.any(pabc, args, target):
            return True
        return False

    @staticmethod
    def jiSum(pabc: LotteryData, args: str, target: str):
        if target == "all":
            jishu = [y for x in pabc.values() for y in x]
        else:
            jishu = pabc[target]
        jiList = [x for x in jishu if x % 2 == 1]
        Number_for_args = CalcUtils.nwped(args)
        if sum(jiList) in Number_for_args:
            return True
        return False

    @staticmethod
    def ouSum(pabc: LotteryData, args: str, target: str):
        if target == "all":
            oushu = [y for x in pabc.values() for y in x]
        else:
            oushu = pabc[target]
        ouList = [x for x in oushu if x % 2 == 0]
        Number_for_args = CalcUtils.nwped(args)
        if sum(ouList) in Number_for_args:
            return True
        return False

    @staticmethod
    def zsSum(pabc: LotteryData, args: str, target: str):
        if target == "all":
            zhishu = [y for x in pabc.values() for y in x]
        else:
            zhishu = pabc[target]
        zs = CalcUtils.zs(max(zhishu))
        zsList = [x for x in zhishu if x in zs]
        Number_for_args = CalcUtils.nwped(args)
        if sum(zsList) in Number_for_args:
            return True
        return False

    @staticmethod
    def hsSum(pabc: LotteryData, args: str, target: str):
        if target == "all":
            heshu = [y for x in pabc.values() for y in x]
        else:
            heshu = pabc[target]
        zs = CalcUtils.zs(max(heshu))
        hsList = [x for x in heshu if x not in zs]
        Number_for_args = CalcUtils.nwped(args)
        if sum(hsList) in Number_for_args:
            return True
        return False

    @staticmethod
    def max(pabc: LotteryData, args: str, target: str):
        if target == "all":
            maxVale = [y for x in pabc.values() for y in x]
        else:
            maxVale = pabc[target]
        maxVale = max(maxVale)
        Number_for_args = CalcUtils.nwped(args)
        if maxVale in Number_for_args:
            return True
        return False

    @staticmethod
    def min(pabc: LotteryData, args: str, target: str):
        if target == "all":
            minVale = [y for x in pabc.values() for y in x]
        else:
            minVale = pabc[target]
        minVale = min(minVale)
        Number_for_args = CalcUtils.nwped(args)
        if minVale in Number_for_args:
            return True
        return False

    @staticmethod
    def lianhao(pabc: LotteryData, args: str, target: str):
        if target == "all":
            targetv = [y for x in pabc.values() for y in x]
        else:
            targetv = pabc[target]
        _lh = CalcUtils.lianhao(targetv)
        Number_for_args = CalcUtils.nwped(args)
        if _lh in Number_for_args:
            return True
        return False

    @staticmethod
    def xiangsidu(pabc: LotteryData, args: str, target: str):
        if target == "all":
            targetv = [y for x in pabc.values() for y in x]
        else:
            targetv = pabc[target]
        cankao, notin = args.split(" ")
        xsdu = CalcUtils.xiangsidu(targetv, cankao)
        notin = CalcUtils.nwped(notin)
        # print(f'{cankao=} {notin=} {xsdu=}')
        if xsdu not in notin:
            return True
        return False


# endregion


# region filter_for_pabc
class filter_for_pabc:
    def __init__(self, filters: list):
        self.filters = filters
        self.filterFunc_data = filterFunc.getFuncName()

    def __get_func(self, func: str):
        temp = [getattr(filterFunc, func), self.filterFunc_data[func]]
        return temp

    def handle(self, pabc: dict):
        """
        pabc {PA:[...],PB:[...]}
        filter = {
            "func": _func,
            "target": _target,
            "condition": _condit,
        }
        """
        flgs = []
        for item in self.filters:
            # 1. 获取函数对象 _f 和 它的参数描述 _p
            # _p 的结构示例: {'parameters': {'pabc': 'LotteryData', 'args': 'str', 'target': 'str'}, ...}
            _f, _p = self.__get_func(func=item["func"])

            # 2. 动态构建参数字典
            args_to_pass = {}

            # n 是参数名 (如 'pabc'), t 是类型名称 (如 'LotteryData')
            for n, t in _p["parameters"].items():
                if n == "pabc":
                    # 传递当前的开奖数据对象
                    args_to_pass[n] = pabc
                elif n == "args":
                    # 传递过滤条件 (例如 "1-10")
                    args_to_pass[n] = item.get("condition", "")
                elif n == "target":
                    # 传递目标位置 (例如 "PA")
                    args_to_pass[n] = item.get("target", "")
                else:
                    # 处理其他可能的参数，或者给个 None 防止报错
                    args_to_pass[n] = None
            try:
                # 3. 使用 ** 解包运行函数
                return_code = _f(**args_to_pass)
                flgs.append(return_code)
            except Exception as e:
                flgs.append(False)
        if False in flgs:
            return False
        return True


# endregion
