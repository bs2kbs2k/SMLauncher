from subprocess import run as srun
import shlex


def run(working_dir, command, cmd_input=None):
    return srun(["cmd", "/c", "set MSYSTEM=MINGW64&&" + "MSYS2/msys2/usr/bin/bash.exe" + " --login -c " +
                shlex.quote("cd {} && {}".format(working_dir, command))], capture_output=True, input=cmd_input)
