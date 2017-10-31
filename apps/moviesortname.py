#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE SORT NAME UPDATER
# ###

# Set the sort name for a M4V movie correctly
#
##########################################################################
import collections
import os

import sys


def check_source_file(check_file):
    """Check the source file for the correct name"""
    result = collections.namedtuple('Result', 'file error')
    if check_file is None:
        return result(None, 'File not supplied')

    if not os.path.isfile(check_file):
        return result(None, 'File is missing %s' % check_file)

    return result(check_file, None)


def main():
    """Main entry point for media name sort updater script"""
    print 'Starting Media Sort Name Updater'
    if len(sys.argv) < 3:
        print 'File name not supplied'
        sys.exit(2)

    source_link = sys.argv[1]
    print 'Loading file %s' % source_link
    source_link = check_source_file(source_link)
    if source_link.error is not None:
        print source_link.error
        sys.exit(1)


if __name__ == "__main__":
    main()
