# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-04-09 07:30:25
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-09 13:03:37
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import List


@dataclass
class Command:
    """
    Command类用于表示一个命令行程序的基本信息,包括名称、描述、用法和是否需要sudo权限。
    该类使用dataclass装饰器简化了类的定义,使得代码更加简洁和易读。
    - name: 命令行程序的名称
    - args: 命令行程序的参数
    - description: 命令行程序的描述信息
    - sudo: 是否需要sudo权限,默认为False
    - result: 命令行程序的执行结果,默认为空字符串
    """

    name: str
    args: str
    description: str
    sudo: bool = False

    def __str__(self):
        command_string = f"{self.name} {self.args}"
        if self.sudo:
            command_string = f"sudo {command_string}"
        return command_string


def Command_Splitting(command: Command) -> List[str]:
    """将命令行字符串分割成列表"""
    return shlex.split(str(command))


def Run_Command(conmand: List) -> str:
    """执行命令行程序并返回Text结果"""
    cmd = Command_Splitting(command=conmand)
    result = subprocess.run(conmand, capture_output=True, text=True)
    return result.stdout


def FletServer(script: str):
    """启动flet服务器"""
    cmd = Command(
        name="flet",
        args=f"run -d --web --port 45678 --ignore '.venv, __pycache__, build, storage, .ruff_cache, assets, storage' {script}",
        description="Start flet server",
        sudo=False,
    )
    # 注意：ignore 列表最好包裹在引号内
    ignore_list = ".venv, __pycache__, build, storage, .ruff_cache, assets, storage"

    cmd = Command(
        name="flet",
        args=f"run -d --web --port 45678 --ignore '{ignore_list}' {script}",
        description="Start flet server",
        sudo=False,
    )

    print(f"Executing: {cmd}")
    cmd_list = Command_Splitting(cmd)

    # 3. 准备日志文件
    # 必须重定向到文件，否则 Python 脚本退出时，flet 会因为没有 stdout 而崩溃
    log_file = open("flet_run.log", "w")

    try:
        process = subprocess.Popen(
            cmd_list,
            stdout=log_file,  # 输出重定向到文件
            stderr=subprocess.STDOUT,  # 错误也重定向到文件
            start_new_session=True,  # 开启新会话，脱离当前终端
            text=True,
        )

        # 4. 等待几秒钟，确认进程没有立即挂掉
        print("检查启动状态...", end="", flush=True)
        time.sleep(3)

        if process.poll() is None:
            print("\n" + "=" * 40)
            print(f"✅ Flet Started successfully!")
        else:
            print(f"\n❌ Flet Startup failed, exit code: {process.poll()}")
            # 失败时尝试读取最后几行日志并打印
            log_file.close()
            with open("flet_run.log", "r") as f:
                print("Error log preview:")
                print(f.readlines()[-10:])  # 打印最后10行

    except Exception as e:
        print(f"\nException occurred during startup: {e}")


def Pids():
    """列出当前系统的所有pid"""
    cmd = Command(
        name="ps",
        args="-e -o pid=",
        description="List all pids in the system",
        sudo=False,
    )
    output = subprocess.check_output(Command_Splitting(cmd)).decode()
    pids = [line.strip() for line in output.splitlines() if line.strip()]
    return pids


def killPid(pid: str):
    """杀死指定pid的进程"""
    pid = pid.strip()
    if not pid:
        return
    cmd = Command(
        name="kill",
        args=f"-9 {pid}",
        description=f"Kill process with pid {pid}",
        sudo=False,
    )
    subprocess.run(Command_Splitting(cmd))
    print(f"kill from pid {pid}")


def SavePids(pids: List[str]):
    """将pids保存到文件中"""
    with open("pids.txt", "w") as f:
        for pid in pids:
            f.write(f"{pid}\n")


def ReadPids() -> List[str]:
    """从文件中读取pids"""
    with open("pids.txt", "r") as f:
        pids = f.read().splitlines()
    return pids


def DifferencePids() -> List[str]:
    """比较当前系统的pids和文件中保存的pids,返回新增的pids"""
    nowPids = set(Pids())
    oldPids = set(ReadPids())
    newPids = nowPids - oldPids
    return [pid for pid in newPids]


def killNewPids():
    """杀死新增的pids"""
    Mypid = SelfAssessment()
    print(f"My pid {Mypid}")
    newPids = DifferencePids()
    for pid in newPids:
        clean_pid = pid.strip()
        try:
            if clean_pid in Mypid:
                print(f"Skipping self/protected process: {clean_pid}")
                continue
            killPid(clean_pid)
        except Exception as e:
            print(f"Failed to kill pid: {pid}, error: {e}")


def SelfAssessment():
    """获取需要保护的 PID 列表"""
    protected = []
    # 1. 当前脚本的 PID
    protected.append(str(os.getpid()))
    # 2. 父进程 PID (通常是 Shell)
    protected.append(str(os.getppid()))
    # 3. 进程组 ID
    try:
        protected.append(str(os.getpgrp()))
    except:
        pass
    return list(set(protected))  # 去重


def main():
    print("Hello, World!")
    if len(sys.argv) < 2:
        print("python script.py [save|diff|run]")
        return

    action = sys.argv[1]
    match action:
        case "save":
            pids = Pids()
            SavePids(pids)
            print(f"Pids saved to pids.txt {len(pids)}")
        case "diff":
            newPids = DifferencePids()
            for i, np in enumerate(newPids):
                print(f"{i:>2}: {np.strip()}")
        case "kill":
            killNewPids()
        case "flet":
            FletServer(sys.argv[2])
        case _:
            pass


if __name__ == "__main__":
    main()
