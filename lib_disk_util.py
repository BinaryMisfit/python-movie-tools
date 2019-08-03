##########################################################################
# DISK LIBRARY
# ###

# Library of file and directory related functions

# Current Version: 0.0.1
##########################################################################
from pathlib import Path

class DiskResult(object):
    """Result return object"""
    def __init__(self, result, data = None, error = None):
        self.result = result
        self.data = data
        self.error = error


def list_all_files(target_folder):
    """List all the files in a folder"""
    folder = Path(target_folder)
    if not folder.exists():
        return DiskResult(False, error = 'Folder missing')
    
    files = folder.glob('**/*') 
    if files is None:
        return DiskResult(False, error = 'No file found')

    return DiskResult(True, data = files)


def check_contains_file(target_folder, target_extension):
    """Checks for a specific set of files in a folder"""
    folder = Path(target_folder)
    if not folder.exists():
        return DiskResult(False, error = 'Folder missing')
    
    files = folder.glob(target_extension)
    if files is None:
        return DiskResult(False, error = 'No file found')

    return DiskResult(True, data = files)


def rename_file(source, target):
    """Rename file"""
    source_file = Path(source)
    if not source_file.exists():
        return DiskResult(False, error = 'File not found %s' % source)

    delete_file(target)
    target_file = Path(target)
    source_file.rename(target_file)
    target_file = Path(target)
    if not target_file.exists():
        return DiskResult(False, error = 'Rename failed')

    return DiskResult(True, data = str(target_file))


def delete_file(target):
    """Delete a file"""
    target_file = Path(target)

    if target_file.exists():
        target_file.unlink()


def file_size_format(num, suffix='B'):
    """Return file size in human readable format"""
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def cmd_exists(cmd):
    """Check if a cmd is installed on the machine"""
    import os
    return any(
        os.access(os.path.join(path, cmd), os.X_OK)
        for path in os.environ["PATH"].split(os.pathsep)
    )