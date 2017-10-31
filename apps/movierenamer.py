#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE RENAMER UPDATER
# ###

# Rename a M4V file and all relevant files and tags
#

# Current Version: 0.0.1
##########################################################################


def read_file_data(file_path):
    """Retrieve file data"""
    import disklibrary
    from dateutil import parser
    from mutagen.mp4 import MP4, MP4StreamInfoError
    try:
        read_file = MP4(file_path.full_path)
        movie_title = read_file['\xa9nam'][0]
        movie_title = disklibrary.path_sane_name(movie_title)
        movie_year = read_file['\xa9day'][0]
        movie_year = parser.parse(movie_year).year
        sort_name = read_file['sonm'][0]
        sort_name = disklibrary.path_sane_name(sort_name)
        sort_name = '%s (%s)' % (sort_name, movie_year)
        movie_file = '%s (%s)' % (movie_title, movie_year)
        movie_file = '%s/%s%s' % (file_path.file_path.replace(file_path.file_title, sort_name),
                                  movie_file, file_path.file_extension)
        movie_file = disklibrary.file_split(movie_file)
        return movie_file
    except MP4StreamInfoError as exception:
        return '%s' % exception.message


def sorted_folder(file_path):
    """Returns the name of the sorted folder"""
    import disklibrary
    from dateutil import parser
    from mutagen.mp4 import MP4, MP4StreamInfoError
    try:
        read_file = MP4(file_path)
        movie_year = read_file['\xa9day'][0]
        movie_year = parser.parse(movie_year).year
        sort_name = read_file['sonm'][0]
        sort_name = disklibrary.path_sane_name(sort_name)
        sort_name = '%s (%s)' % (sort_name, movie_year)
    except MP4StreamInfoError as exception:
        return '%s' % exception.message
    return sort_name


def rename_movie(source_file):
    """Rename movie folder and content"""
    import os
    import disklibrary
    file_path = disklibrary.file_check(source_file, 'm4v')
    if file_path is None:
        print 'File not found or incorrect type'
        return 2

    file_path = disklibrary.file_split(file_path)
    rename_file = read_file_data(file_path)
    if not rename_file:
        print 'No file can be found'
        return 2

    file_list = os.listdir(file_path.file_path)
    for file_name in file_list:
        if file_name == '.DS_Store':
            continue

        file_name = disklibrary.file_path(file_path.file_path, file_name)
        file_name = disklibrary.file_split(file_name)
        file_rename = file_name.file_title.replace(
            file_path.file_title, rename_file.file_title)
        file_rename += file_name.file_extension
        file_rename = disklibrary.file_path(file_name.file_path, file_rename)
        file_rename = disklibrary.file_split(file_rename)
        if file_name.file_name != file_rename.file_name:
            print 'Renaming file %s' % file_name.file_name
            os.rename(file_name.full_path, file_rename.full_path)

    if os.path.isdir(rename_file.file_path):
        return 0

    print 'Renaming folder %s to %s' % (file_path.file_path, rename_file.file_path)
    if os.path.isdir(file_path.file_path) and not os.path.isdir(rename_file.file_path):
        os.rename(file_path.file_path, rename_file.file_path)

    return 0


def main():
    """Renames an M4V file all additional files"""
    import sys
    import argparse
    print 'Starting Movie Renamer'
    parser = argparse.ArgumentParser(
        description='Renames a M4V file and all relevant files and tags')
    parser.add_argument('file', metavar='file', type=str,
                        help='File to be renamed')
    args = parser.parse_args()
    print 'Checking file %s' % args.file
    output = rename_movie(args.file)
    sys.exit(output)


if __name__ == '__main__':
    main()
