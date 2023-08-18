#!/usr/bin/env /lamport/shared/hzzhu/miniforge3/envs/zlaunch/bin/python

import os
import subprocess
import sys
import argparse

QUEUE_CHOICES = ['h', 'b', 'm', 'hopfield', 'boltzmann', 'makkapakka', 'debug']

USER_NOTICE = 'zlaunch大体上遵循了ilaunch的用法；由于Argparser的限制，在输入最后需要提交执行的命令前一般需要插入" -- "，例如：zlaunch -q hopfield -- vcs -ID'

parser = argparse.ArgumentParser(prog='zluanch', description='Run anything on LSF queues.',
                                 epilog=USER_NOTICE)
parser.add_argument("--lfs", action='store_true', help="Use LFS instead of the default SLURM scheduler.")
parser.add_argument("-p", "--purge", dest="purge", action="store_true", help="Purge all the loaded modules before loading.")
parser.add_argument("-l", "--load", dest="load", action="append", metavar="MODULE", help="Load modules (available modules refer to 'module av').")
parser.add_argument("-q", "--queue", dest="queue", choices=QUEUE_CHOICES, default='hopfield', help="Select an LSF queue to launch.")
parser.add_argument("--gpu", dest="gpu", metavar='ID_LIST', type=str, help="Set visible GPU ids, such as '0,1,2,3'")
parser.add_argument("--env", dest="env", type=str, help="Environment variables, A=1,B=2")
parser.add_argument("--list", dest="list", action='store_true', help="Print modules now loaded.")
parser.add_argument("--args", dest="args", type=str, action='append', default=[''], help="Extra args to be set when bsub/srun.")
parser.add_argument("command", nargs="*", help="Command to be submitted and executed.")

args = parser.parse_args()

commands = []

# ==================================================================================================
# Prepare args

if args.lfs:
    if args.queue == 'h':
        args.queue = 'hopfield'
    elif args.queue == 'b':
        args.queue = 'boltzmann'
    elif args.queue == 'm':
        args.queue = 'makkapakka'
else:
    print('SLURM has only one queue (partition): debug')
    args.queue = 'debug'

bsub_args = ' '.join(args.args)
if args.gpu is not None:
    if args.queue != "makkapakka":
        print(f"Warn: <{args.queue}> does NOT accept GPU tasks. Submitted to <makkapakka>.")
        args.queue = 'makkapakka'
    if args.lfs:
        bsub_args += f' CUDA_VISIBLE_DEVICES={args.gpu}'
    else:
        gpu_count = len(args.gpu.replace(',', ''))
        bsub_args += f'--gpus={args.gpu}'

if args.env is not None:
    if args.lfs:
        bsub_args += f'-env all,{args.env}'
    else:

        bsub_args += f'--export=ALL,{args.env}'


# ==================================================================================================
# Process EDA module loading
if args.purge:
    print("All modules purged before loading.")
    commands += ["module purge"]

if args.load is not None:
    modules = " ".join(args.load)
    commands += [f"module load {modules}"]

if args.list:
    commands += ["module list"]

# ==================================================================================================
# Submit commands to queue

bsub_cmd = ' '.join(args.command)
if bsub_cmd != '':
    if args.lfs:
        cmd = f"bsub -q {args.queue} -Is -env {args.env} {bsub_args} {bsub_cmd}"
    else:
        if 'DISPLAY' in os.environ:
            os.environ['DISPLAY'] = 'mgmt01:20'
        cmd = f"srun --pty --partition={args.queue} {bsub_args} {bsub_cmd}"
    commands += [cmd]

cmd = ";\n   ".join(commands)
if cmd != '':
    print(f"Executing command >>>> \n   {cmd}\n")
    subprocess.call(cmd, shell=True, executable="/usr/bin/bash", env=os.environ)
else:
    print('Command is empty, so nothing will be submitted or executed.')
sys.exit()
