<h1 align=center> zLaunch </h1>
<div align="center">

**Just submit and run tasks on FICS**

</div>

zLaunch（`zlaunch`）是对 ilaunch 的 Python 实现。zLaunch 大体上遵循了 ilaunch 的用法，改善了它的环境变量传输、EDA module 加载等。

（之所以需要用 Python 重写，是因为我看不懂帅 kun 的 Tcl 脚本。）

## 如何在服务器上使用 zLaunch ？

### 选择 1. 使用我放在 FICS 上的脚本

该脚本在 FICS 服务器我的 `Lamport` 目录上已有一份拷贝，因此你可以把它加入你的 `PATH` 环境变量：
```shell
# in your .bashrc/.zshrc
export PATH="/capsule/home/hzzhu/Software/zlaunch:$PATH"
```

如果你已经使用了我的 EDA 环境，那它天然就已经在你的 `PATH` 里了。

### 选择 2. 使用你自己的魔改版本

你也可以 clone 这个仓库，然后自己修改。毕竟人人都会写 Python，不行的话 ChatGPT。

## 如何使用 zLaunch 提交任务？

### 太长不看

```shell
# 默认队列（hopfield）
zlaunch -- verdi
# 指定队列
zlaunch -q hopfield -- verdi
```

### 详细解释

查看帮助：`zlaunch -h` 或 `zlaunch --help`。
```
usage: zluanch [-h] [--lfs] [-p] [-l MODULE] [-q {h,b,m,hopfield,boltzmann,makkapakka}] [--gpu ID_LIST] [--env ENV] [--list] [--args ARGS] [command ...]
options:
  -h, --help            show this help message and exit
  --lfs                 Use LFS instead of the default SLURM scheduler.
  -p, --purge           Purge all the loaded modules before loading.
  -l MODULE, --load MODULE
                        Load modules (available modules refer to 'module av').
  -q {h,b,m,hopfield,boltzmann,makkapakka}, --queue {h,b,m,hopfield,boltzmann,makkapakka}
                        Select an LSF queue to launch.
  --gpu ID_LIST         Set visible GPU ids, such as '0,1,2,3'
  --env ENV             Environment variables, A=1,B=2
  --list                Print modules now loaded.
  --args ARGS           Extra args to be set when bsub/srun.
```

如上所示，`zlaunch` 命令具有以下参数：
|参数|说明|
|----|---|
|`--lfs`| 使用 LFS.bsub 提交任务，否则默认将使用 SLURM.srun。目前两者能调度的服务器范围有区别，未来将逐步淘汰 LFS。 |
|`-p` 或 `--purge`| 在提交任务前卸载所有 module（需搭配 `--load` 参数使用）。 |
|`-l MODULE` 或 `--load MODULE`| 在提交任务前加载该 module。 |
|`-q QUEUE`或`--queue QUEUE`| 指定提交的队列，可以是 `h`（`hopfield`）、`b`（`boltzmann`）、`m`（`makkapakka`），默认是 `hopfield`。|
|`--gpu ID_LIST`|指定GPU，例如四张卡就写 `--gpu 0,1,2,3`，这个接口未来会改。现阶段只有 LFS 可以调度到 GPU 队列。|
|`--env A=1,C=2`|指定环境变量，复杂规则可以看 `srun` 的文档。原则上不需要修改，zLaunch会将本地的当前环境变量提交到节点上。|
|`--list`| 提交前首先打印 `module list`。如果你不是使用我的 EDA 环境，这个参数对你不一定有意义。|
|`--args XXX`| 这里的 XXX 会直接作为 srun（或bsub）的参数，用于用户精细化控制提交任务的行为。一般用不上，当你需要调这个了，建议不要用zLaunch了，自己手写srun（或bsub）命令比较合适。|

最后附上你要执行的任务。在任务和参数中间，建议加一个`--`符号隔断，像这样：

```shell
zlaunch --list -q hopfield -- verdi
```

## 已知问题

该脚本是 Python 编写的，因此需要执行任务的节点上能够执行 Python3 脚本。大部分节点服务器上都只有一个古老的 Python2，因此我在脚本的第一行中指定了一个我预置在 `/lamport/shared/hzzhu/..` 目录下的 Python 环境。

如果你发现你提交任务的节点，无法访问到这个目录，那可能是这个服务器无法访问 `lamport`，请联系我或者管理员。
