from os.path import abspath, realpath, dirname, join as joinpath
from sys import stderr


def resolved(x):
    return realpath(abspath(x))


def badpath(path, base):
    # joinpath will ignore base if path is absolute
    return not resolved(joinpath(base, path)).startswith(base)


def badlink(info, base):
    # Links are interpreted relative to the directory containing the link
    tip = resolved(joinpath(base, dirname(info.name)))
    return badpath(info.linkname, base=tip)


def safemembers(members, logfile):
    base = resolved(".")

    for finfo in members:
        if badpath(finfo.name, base):
            print(stderr, finfo.name, "is blocked (illegal path)", file=logfile)
        elif finfo.issym() and badlink(finfo, base):
            print(stderr, finfo.name, "is blocked: Hard link to", finfo.linkname, file=logfile)
        elif finfo.islnk() and badlink(finfo, base):
            print(stderr, finfo.name, "is blocked: Symlink to", finfo.linkname, file=logfile)
        else:
            yield finfo
