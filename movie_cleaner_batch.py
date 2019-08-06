#!/usr/bin/env python

##########################################################################
# Movie Cleaner
# ###

# Script to clean movie files and folders

# Current Version: 0.0.1
##########################################################################
from movie_cleaner import process_folder
from pathlib import Path


class BatchFolder(object):
    """Object containing all information for the script"""

    def __init__(self, folder_name, result='', error=False):
        self.folder_name = folder_name
        self.result = result
        self.error = error

    def __repr__(self):
        return '<BatchFolder folder_name: {3}, result: {8}, ' \
            ' error: {9}>'.format(self.folder_name, self.result,
                                  self.error)

    def __str__(self):
        return repr(self)


def process(folder):
    """Process and iterate through the specified folder"""
    from termcolor import colored
    batch = BatchFolder(folder)
    batch_folder = Path(batch.folder_name)
    if not batch_folder.exists():
        batch.error = True
        batch.result = 'Folder not found'
        return batch

    if not batch_folder.is_dir():
        batch.error = True
        batch.result = 'Not a folder'
        return batch

    print('Checking:\t\t{0}', batch.folder_name)
    print(colored("=================================", 'blue'))
    print('Processing:\t\t{0}', batch.folder_name)
    print(colored("=================================", 'blue'))
    return batch


def main():
    """Main entry point for script"""
    from colorama import init
    from termcolor import colored
    import sys
    import argparse
    init()
    parser = argparse.ArgumentParser(
        description='Clean all movies stored in specified folder')
    parser.add_argument('folder', metavar='folder', type=str,
                        help='Folder to check')
    args = parser.parse_args()
    movie = process(args.folder)
    if movie.error:
        print('Error\t\t{0}').format(colored(movie.result, 'red'))
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
