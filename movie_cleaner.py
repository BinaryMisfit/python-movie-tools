#!/usr/bin/env python

##########################################################################
# Movie Cleaner
# ###

# Script to clean movie files and folders

# Current Version: 0.0.1
##########################################################################


class MovieFolder(object):
    """Object containing all information for the script"""

    def __init__(self, mkv_file, folder_name=None, parent=None,
                 has_img=False, has_nfo=False, has_srt=False, result='',
                 error=False):
        self.mkv_file = mkv_file
        self.folder_name = folder_name
        self.parent = parent
        self.has_img = has_img
        self.has_nfo = has_nfo
        self.has_srt = has_srt
        self.result = result
        self.error = error

    def __repr__(self):
        return '<MovieFolder mkv_file: %s, folder_name: %s, parent: %s, ' \
            'has_img: %r, has_nfo: %r, has_srt: %r, result: %s, error: %r>' % \
            (self.mkv_file, self.folder_name, self.parent, self.has_img,
             self.has_nfo, self.has_srt, self.result, self.error)

    def __str__(self):
        return repr(self)


def validate_mkv(file):
    """Check if the MKV file exists and populate MovieFolder"""
    from pathlib import Path
    mkv_file = Path(file)
    movie_folder = MovieFolder(mkv_file)
    if not mkv_file.exists():
        movie_folder.result = "File not found"
        movie_folder.error = True
        return movie_folder

    movie_folder.folder_name = mkv_file.parent.name
    movie_folder.parent = mkv_file.parent
    movie_folder.has_img = sum(1 for x in mkv_file.glob('*.jpg')) > 0
    movie_foider.has_nfo = sum(1 for x in mkv_file.glob('*.nfo')) > 0
    movie_folder.has_srt = sum(1 for x in mkv_file.glob('*.srt')) > 0
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

    print(movie)
    output = 0
    sys.exit(output)


if __name__ == '__main__':
    main()
