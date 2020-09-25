import wget
import os.path
import shutil


def download(url, out_dir, cache_dir="cache/"):
    with open(os.path.join(cache_dir, "cache.txt"), 'r+') as file:
        lines = file.readlines()
        if url+'\n' not in lines:
            file_name = wget.download(url, cache_dir, lambda a, b, c: None)
            file.writelines([url, '\n', file_name, '\n'])
            shutil.copy2(file_name, out_dir)
            return os.path.join(out_dir, file_name.split(os.path.sep)[-1])
        else:
            file_name = lines[lines.index(url+'\n') + 1][:-1]
            shutil.copy2(file_name, out_dir)
            return os.path.join(out_dir, file_name.split(os.path.sep)[-1])
