import shutil
import os.path


def cp(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def cp_list(lst, dst):
    for a in lst:
        cp(a, dst)


def win_to_msys(path):
    abspath = os.path.abspath(path)
    seppedpath = os.path.split(abspath)
    seppedpath[0] = seppedpath[0][0].lower()
    escapedpath = [a.replace('/', '\\/') for a in seppedpath]
    return '/' + '/'.join(escapedpath)