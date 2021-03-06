from subprocess import run as srun
import subprocess
import shlex


def run(command, working_dir='', cmd_input=None):
    return srun(["cmd", "/c", "set MSYSTEM=MINGW64&& MSYS2/msys2/usr/bin/bash.exe --login -c " +
                 shlex.quote("cd {} && {}".format(working_dir, command))],
                capture_output=True, input=cmd_input, stderr=subprocess.STDOUT, text=True).stdout


def r(log, command, working_dir='', cmd_input=None):
    print(run(command, working_dir, cmd_input), file=log)
