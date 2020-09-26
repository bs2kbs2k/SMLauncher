import subprocess
from os.path import join, normpath

import dlmgr
import tarfile
import safetar
from shellinteract import InteractiveShell


class Builder:
    def __init__(self, build_type, build_dir, log_file):
        self.build_type = build_type
        self.build_dir = build_dir
        self.log_file = log_file

    def prepare(self, reused=None):
        """returns a list of files and folders to be reused."""
        raise NotImplementedError()

    def apply_patches(self, patches):
        """applies patches. must be called after prepare()."""
        raise NotImplementedError()

    def build(self):
        """builds. must be called after apply_patches. returns the path to the executable."""
        raise NotImplementedError()


class MSYS2Builder(Builder):
    URL = "https://github.com/msys2/msys2-installer/releases/download/nightly-x86_64/msys2-base-x86_64-latest.tar.xz"

    def __init__(self, build_type, build_dir, log_file):
        super().__init__(build_type, build_dir, log_file)

    def prepare(self, reused=None):
        file = dlmgr.download(MSYS2Builder.URL, self.build_dir)
        log_file = open(self.log_file, 'a')
        with tarfile.open(file) as f:
            f.extractall(self.build_dir, members=safetar.safemembers(f, log_file))
        print('Running MSYS2 first startup...', file=log_file)
        shell = InteractiveShell(["cmd", "/c", "set MSYSTEM=MINGW64&& set PS1=shell_prompt$&& {} --login"
                                 .format(join(self.build_dir, normpath('msys2/usr/bin/bash.exe')))],
                                 'shell_prompt$', log_file)
        shell.stop()
        print('Updating MSYS2...', file=log_file)
        shell = InteractiveShell(["cmd", "/c", "set MSYSTEM=MINGW64&& set PS1=shell_prompt$&& {} --login"
                                 .format(join(self.build_dir, normpath('msys2/usr/bin/bash.exe')))],
                                 'shell_prompt$', log_file)
        shell.execute_and_get_output('pacman -Syu')
        print('Installing dependencies...', file=log_file)
        shell.execute_and_get_output('pacman -S --noconfirm {}'.format(self.build_type['deps']['MSYS2']))
        print('Cloning the repository...', file=log_file)
        shell.execute_and_get_output('cd')
        shell.execute_and_get_output(
            'git clone {} {} portrepo'.format(self.build_type['cloneopts'], self.build_type['repo']))
        shell.execute_and_get_output('cd portrepo')
