#!/usr/bin/env /lamport/shared/hzzhu/miniforge3/envs/zlaunch/bin/python

import os
import subprocess
import sys
import argparse
import socket

QUEUE_CHOICES = ['h', 'b', 'm', 'hopfield', 'boltzmann', 'makkapakka']

DESCRIPTION = 'zLaunch 是 ilaunch 的 Python 实现，帮助用户在 FICS 集群运行 EDA 任务。完整文档在 github.com/cihlab/zlaunch。'
USER_NOTICE = '在输入需要提交执行的命令前一般需要插入" -- "，例如：zlaunch -q hopfield -- vcs -ID。'
DEFAULT_CPU_NUM = 10

parser = argparse.ArgumentParser(prog='zluanch', description=DESCRIPTION, epilog=USER_NOTICE)
parser.add_argument("-p", "--purge", dest="purge", action="store_true", help="Purge all the loaded modules before loading.")
parser.add_argument("-l", "--load", dest="load", action="append", metavar="MODULE", help="Load modules (available modules refer to 'module av').")
parser.add_argument("-q", "--queue", dest="queue", choices=QUEUE_CHOICES, default='hopfield', help="Select an SLURM queue to launch.")
parser.add_argument("--cpu", dest="cpu", metavar='NUM', type=int, default=DEFAULT_CPU_NUM, help=f"Set wanted CPU core number. default: {DEFAULT_CPU_NUM}")
parser.add_argument("--gpu", dest="gpu", metavar='NUM', type=int, help="Set wanted GPU number, such as 3")
parser.add_argument("--env", dest="env", type=str, help="Environment variables, A=1,B=2")
parser.add_argument("--list", dest="list", action='store_true', help="Print modules now loaded.")
parser.add_argument("--args", dest="args", type=str, action='append', default=[''], help="Extra args to be set when srun.")
parser.add_argument("command", nargs="*", help="Command to be submitted and executed.")

args = parser.parse_args()

# ==================================================================================================
# Prepare args

if args.queue == 'h':
    args.queue = 'hopfield'
elif args.queue == 'b':
    args.queue = 'boltzmann'
elif args.queue == 'm':
    args.queue = 'makkapakka'

scheduler_args = ' '.join(args.args)
if args.env is not None:
    scheduler_args += f'--export=ALL,{args.env} '
else:
    scheduler_args += '--export=ALL '

if args.gpu is not None:
    scheduler_args += f'--gpus={args.gpu} '
    if args.queue != "makkapakka":
        print(f"Warn: <{args.queue}> does NOT accept GPU tasks. Submitted to <makkapakka>.")
        args.queue = 'makkapakka'

# ==================================================================================================
# Prepare commands

commands = []

if args.purge:
    print("All modules purged before loading.")
    commands += ["module purge"]

if args.load is not None:
    modules = " ".join(args.load)
    commands += [f"module load {modules}"]

if args.list:
    commands += ["module list"]

user_cmd = ' '.join(args.command)
if user_cmd != '':
    if 'DISPLAY' in os.environ:
        hostname = socket.gethostname()
        os.environ['DISPLAY'] = f'{hostname}:01'
    commit_cmd = f"srun --pty -c {args.cpu} -p {args.queue} {scheduler_args} {user_cmd}"
    commands += [commit_cmd]

# ==================================================================================================
# Submit commands to queue

if commands:
    cmd = ";\n   ".join(commands)
    print(f"Executing command >>>> \n   {cmd}\n")
    subprocess.call(cmd, shell=True, executable="/usr/bin/bash", env=os.environ)
else:
    print('Command is empty, so nothing will be submitted or executed.')
sys.exit()
