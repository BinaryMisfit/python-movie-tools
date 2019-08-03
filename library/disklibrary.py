#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# DISK LIBRARY
# ###

# Library of file and directory related functions

# Current Version: 0.0.2
##########################################################################


def file_first(check_folder, file_type=None):
    """Check for the first file in a folder"""
    import os
    if not os.path.isdir(check_folder):
        return None

    for file_found in os.listdir(check_folder):
        file_found = file_path(check_folder, file_found)
        if file_type is None:
            return file_check(file_found)

        file_ext = file_split(file_found).file_extension
        if file_ext == '.' + file_type:
            file_found = file_check(file_found, file_type)
            return file_check(file_found, file_type)


def file_check(check_file, file_type=None):
    """Check if the file has the required extension"""
    import os
    if check_file is None:
        return None

    check_file = os.path.abspath(check_file)
    if not os.path.isfile(check_file):
        return None

    if file_type is not None:
        file_ext = file_split(check_file).file_extension
        if file_ext != '.' + file_type:
            return None

    return check_file


def file_split(check_path):
    """Split the path into separate parts"""
    import os
    import collections
    if check_path is None:
        return None

    result = collections.namedtuple(
        'file_parts', 'file_path file_name file_title file_extension full_path')
    file_folder, file_name = os.path.split(check_path)
    file_title, file_extension = os.path.splitext(file_name)
    return result(file_folder, file_name, file_title, file_extension, check_path)


def file_delete(remove_file):
    """Delete a specific file"""
    import os
    remove_file = file_check(remove_file)
    if remove_file is None:
        return

    os.remove(remove_file)


def file_write(file_name, content):
    """Write a new file with data"""
    with open(file_name, 'a') as text_file:
        text_file.write(content)


def file_path(file_folder, file_name):
    """Determine the full path to a file"""
    import os
    full_path = os.path.join(file_folder, file_name)
    full_path = file_split(full_path)
    file_folder = path_sane_name(full_path.file_path)
    file_name = path_sane_name(full_path.file_title)
    file_name = file_name + full_path.file_extension
    full_path = os.path.join(file_folder, file_name)
    return full_path


def file_rename(source_file, target_file):
    """Rename a file"""
    import os
    source_file = file_check(source_file)
    if source_file is None:
        return False

    if file_check(target_file) is not None:
        file_delete(target_file)

    os.rename(source_file, target_file)
    return True


def path_sane_name(path_name):
    """Ensure a path name does not contain invalid characters"""
    return "".join([c for c in path_name if c.isalpha() or c.isdigit() or c == ' ' or c == '/'
                    or c == '(' or c == ')' or c == '-' or c == '&']).rstrip()


def cmd_exists(cmd):
    """Check if a cmd is installed on the machine"""
    import os
    return any(
        os.access(os.path.join(path, cmd), os.X_OK)
        for path in os.environ["PATH"].split(os.pathsep)
    )
