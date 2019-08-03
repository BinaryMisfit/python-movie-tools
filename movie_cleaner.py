#!/usr/bin/env python

##########################################################################
# Movie Cleaner
# ###

# Script to clean movie files and folders

# Current Version: 0.0.1
##########################################################################
from pathlib import Path


class MovieFolder(object):
    """Object containing all information for the script"""

    def __init__(self, mkv_file, folder_name=None, parent=None,
                 needs_clean=False, new_parent=False, needs_quality=False, result='',
                 error=False):
        self.mkv_file = mkv_file
        self.folder_name = folder_name
        self.parent = parent
        self.needs_clean = needs_clean 
        self.new_parent = new_parent 
        self.needs_quality = needs_quality 
        self.result = result
        self.error = error

    def __repr__(self):
        return '<MovieFolder mkv_file: %s, folder_name: %s, parent: %s, ' \
            'needs_clean: %r, new_parent: %r, needs_quality: %r, result: %s, error: %r>' % \
            (self.mkv_file, self.folder_name, self.parent, self.needs_clean,
             self.new_parent, self.needs_quality, self.result, self.error)

    def __str__(self):
        return repr(self)


def validate_mkv(file):
    """Check if the MKV file exists and populate MovieFolder"""
    mkv_file = Path(file)
    movie_folder = MovieFolder(mkv_file)
    if not mkv_file.exists():
        movie_folder.result = "Failed - File not found"
        movie_folder.error = True
        return movie_folder

    if mkv_file.is_dir():
        movie_folder.result = "Failed - Specify MKV File"
        movie_folder.error = True
        return movie_folder

    if not mkv_file.suffix == '.mkv':
        movie_folder.result = "Failed - Not a MKV file"
        movie_folder.error = True
        return movie_folder

    movie_folder.folder_name = mkv_file.parent.name
    movie_folder.parent = mkv_file.parent
    mkv_parent = Path(movie_folder.parent)
    list_files = []
    list_files.extend(mkv_parent.glob('*.jpg'))
    list_files.extend(mkv_parent.glob('*.nfo'))
    list_files.extend(mkv_parent.glob('*.srt'))
    print('Files found: %d' % list_files.count)
    needs_clean = int(list_files.count) > 0 
    movie_folder.needs_clean = needs_clean
    movie_folder.new_parent = not mkv_file.name == movie_folder.folder_name
    movie_folder.needs_quality = not '[' in mkv_file.name and not ']' in mkv_file.name
    return movie_folder


def clean_movie_folder(movie_folder):
    clean_folder = Path(movie_folder.parent)
    clean_files = []
    clean_files.extend(clean_folder.glob('*.jpg'))
    clean_files.extend(clean_folder.glob('*.nfo'))
    clean_files.extend(clean_folder.glob('*.srt'))
    for clean_file in clean_files:
        print(clean_file.name)

    movie_folder.needs_clean = False
    return movie_folder


def main():
    """Main entry point for script"""
    import sys
    import argparse
    print 'Starting Movie Renamer'
    parser = argparse.ArgumentParser(
        description='Clean a MKV file name and all relevant files and tags')
    parser.add_argument('file', metavar='file', type=str,
                        help='MKV file to clean')
    args = parser.parse_args()
    print('MKV File\t\t%s' % args.file)
    movie = validate_mkv(args.file)
    if movie.error:
        print('Validation:\t\t%s' % movie.result)
    else:
        print('Validation:\t\tSuccess')

    if movie.needs_clean:
        if not movie.error:
            movie = clean_movie_folder(movie)
            print('Cleanup:\t\tSuccess')
        else:
            print('Cleanup:\t\tFailed')
    else:
        print('Cleanup:\t\tSkipped')

    print(movie)
    output = 0
    sys.exit(output)


if __name__ == '__main__':
    main()
