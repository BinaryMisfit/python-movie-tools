##########################################################################
# DISK LIBRARY
# ###

# Library of file and directory related functions

# Current Version: 0.0.1
##########################################################################
from collections import namedtuple
from pathlib import Path


def list_all_files(target_folder):
    result = namedtuple('Result', 'Error')
    folder = Path(target_folder)
    if not folder.exists():
        return result(None, 'Folder missing')
    
    return result(folder.glob('**/*'), None)


def check_contains_file(target_folder, target_extension):
    result = namedtuple('Result', 'Error')
    folder = Path(target_folder)
    if not folder.exists():
        return result(None, 'Folder missing')
    
    return result(folder.glob(target_extension), None)


def file_size_format(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
