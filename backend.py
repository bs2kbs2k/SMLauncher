import tarfile
from os.path import join, normpath

import dlmgr
import filelib
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
        shell.execute_and_get_output('cd {}'.format(filelib.win_to_msys(self.build_dir)))
        shell.execute_and_get_output(
            'git clone {} {} portrepo'.format(self.build_type['cloneopts'], self.build_type['repo']))
        shell.execute_and_get_output('cd portrepo')
        if reused:
            filelib.cp_list(reused, filelib.win_to_msys(self.build_dir) + '/portrepo/')
            shell.stop()
            return reused
        print('Preparing...', file=log_file)
        shell.execute_and_get_output(self.build_type["prepare_cmd"])
        ret = shell.execute_and_get_output(self.build_type["list_reusable"])
        shell.stop()
        return ret.split('\n')[:-1]

    def apply_patches(self, patches):
        log_file = open(self.log_file, 'a')
        shell = InteractiveShell(["cmd", "/c", "set MSYSTEM=MINGW64&& set PS1=shell_prompt$&& {} --login"
                                 .format(join(self.build_dir, normpath('msys2/usr/bin/bash.exe')))],
                                 'shell_prompt$', log_file)
        shell.execute_and_get_output('cd {}/portrepo'.format(filelib.win_to_msys(self.build_dir)))
        shell.execute_and_get_output('mkdir patches')
        allots = []
        for patch in patches:
            ots = patch.list_overwrites()
            for ot in ots:
                if ot in allots:
                    shell.stop()
                    raise RuntimeError('Overwrite conflict on {}'.format(patch.name))
                allots.append(ot)
            shell.execute_and_get_output('mkdir patches/{}'.format(patch.id))
            patch.extract(filelib.win_to_msys(self.build_dir) + '/portrepo/patches/{}/'.format(patch.id))
            out = shell.execute_and_get_output(
                '{} {} && echo COMPLETE WITHOUT ERRORS'.format(self.build_type["patchcmd"], filelib.win_to_msys(
                    self.build_dir) + '/portrepo/patches/{}/patches.patch'.format(patch.id)))
            if 'COMPLETE WITHOUT ERRORS' not in out:
                shell.stop()
                raise RuntimeError('Patch failed on {}'.format(patch.name))
            shell.execute_and_get_output('cp -t . patches/{}/overwrites/*')
        shell.stop()

    def build(self):
        log_file = open(self.log_file, 'a')
        shell = InteractiveShell(["cmd", "/c", "set MSYSTEM=MINGW64&& set PS1=shell_prompt$&& {} --login"
                                 .format(join(self.build_dir, normpath('msys2/usr/bin/bash.exe')))],
                                 'shell_prompt$', log_file)
        shell.execute_and_get_output('cd {}/portrepo'.format(filelib.win_to_msys(self.build_dir)))
        shell.execute_and_get_output('make {}'.format(self.build_type["makeflags"]))


class PRootBuilder(Builder):
    URL = "https://github.com/proot-me/proot-static-build/raw/master/static/proot-x86_64"

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
        shell.execute_and_get_output('cd {}'.format(filelib.win_to_msys(self.build_dir)))
        shell.execute_and_get_output(
            'git clone {} {} portrepo'.format(self.build_type['cloneopts'], self.build_type['repo']))
        shell.execute_and_get_output('cd portrepo')
        if reused:
            filelib.cp_list(reused, filelib.win_to_msys(self.build_dir) + '/portrepo/')
            shell.stop()
            return reused
        print('Preparing...', file=log_file)
        shell.execute_and_get_output(self.build_type["prepare_cmd"])
        ret = shell.execute_and_get_output(self.build_type["list_reusable"])
        shell.stop()
        return ret.split('\n')[:-1]

    def apply_patches(self, patches):
        log_file = open(self.log_file, 'a')
        shell = InteractiveShell(["cmd", "/c", "set MSYSTEM=MINGW64&& set PS1=shell_prompt$&& {} --login"
                                 .format(join(self.build_dir, normpath('msys2/usr/bin/bash.exe')))],
                                 'shell_prompt$', log_file)
        shell.execute_and_get_output('cd {}/portrepo'.format(filelib.win_to_msys(self.build_dir)))
        shell.execute_and_get_output('mkdir patches')
        allots = []
        for patch in patches:
            ots = patch.list_overwrites()
            for ot in ots:
                if ot in allots:
                    shell.stop()
                    raise RuntimeError('Overwrite conflict on {}'.format(patch.name))
                allots.append(ot)
            shell.execute_and_get_output('mkdir patches/{}'.format(patch.id))
            patch.extract(filelib.win_to_msys(self.build_dir) + '/portrepo/patches/{}/'.format(patch.id))
            out = shell.execute_and_get_output(
                '{} {} && echo COMPLETE WITHOUT ERRORS'.format(self.build_type["patchcmd"], filelib.win_to_msys(
                    self.build_dir) + '/portrepo/patches/{}/patches.patch'.format(patch.id)))
            if 'COMPLETE WITHOUT ERRORS' not in out:
                shell.stop()
                raise RuntimeError('Patch failed on {}'.format(patch.name))
            shell.execute_and_get_output('cp -t . patches/{}/overwrites/*')
        shell.stop()

    def build(self):
        log_file = open(self.log_file, 'a')
        shell = InteractiveShell(["cmd", "/c", "set MSYSTEM=MINGW64&& set PS1=shell_prompt$&& {} --login"
                                 .format(join(self.build_dir, normpath('msys2/usr/bin/bash.exe')))],
                                 'shell_prompt$', log_file)
        shell.execute_and_get_output('cd {}/portrepo'.format(filelib.win_to_msys(self.build_dir)))
        shell.execute_and_get_output('make {}'.format(self.build_type["makeflags"]))
