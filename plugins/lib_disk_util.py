##########################################################################
# DISK LIBRARY
# ###

# Library of file and directory related functions

# Current Version: 0.0.1
##########################################################################
from pathlib import Path

class DiskResult(object):
    def __init__(self, result, data = None, error = None):
        self.result = result
        self.data = data
        self.error = error


def list_all_files(target_folder):
    folder = Path(target_folder)
    if not folder.exists():
        return DiskResult(False, error = 'Folder missing')
    
    return DiskResult(True, data = folder.glob('**/*'))


def check_contains_file(target_folder, target_extension):
    folder = Path(target_folder)
    if not folder.exists():
        return DiskResult(False, error = 'Folder missing')
    
    return DiskResult(True, data = folder.glob(target_extension))


def file_size_format(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
