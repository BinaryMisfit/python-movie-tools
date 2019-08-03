#!/usr/bin/env python

##########################################################################
# Movie Cleaner
# ###

# Script to clean movie files and folders

# Current Version: 0.0.1
##########################################################################


class MovieFolder(object):
    """Object containing all information for the script"""

    def __init__(self, mkv_file, result='', error=False):
        self.mkv_file = mkv_file
        self.result = result
        self.error = error

    def __repr__(self):
        return '<MovieFolder mkv_file: %s, result = %s, error = %r>' % \
            self.mkv_file, self.result, self.error

    def __str__(self):
        return repr(self)


def validate_mkv(file):
    """Check if the MKV file exists and populate MovieFolder"""
    from pathlib import Path
    mkv_file = Path(file)
    movie_folder = MovieFolder(mkv_file)
    print(movie_folder)
    if not mkv_file.exists():
        movie_folder.result = "File not found"
        movie_folder.error = True
        return movie_folder

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
    print(movie)
    if movie.error:
        print('Validation:\t\t%s' % movie.result)
    else:
        print('Validation:\t\tSuccess')

    output = 0
    sys.exit(output)


if __name__ == '__main__':
    main()
