#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# COLLECTION SCANNER
# ###

# Checks a folder of movies to find collections and determine if any movies are missing
#
# Current Version: 0.0.1
##########################################################################


def main():
    """Main script interface for Collection Scanner"""
    import os
    import sys
    import argparse
    print 'Starting Collection Scanner'
    parser = argparse.ArgumentParser(
        description='Checks for movies in collection and lists missing movies')
    parser.add_argument('folder', metavar='folder',
                        type=str, help='Folder to be checked')
    args = parser.parse_args()
    source_folder = args.folder
    if source_folder is None or not os.path.isdir(source_folder):
        print 'Folder %s not found or valid' % source_folder
        sys.exit(2)

    content_list = os.listdir(source_folder)
    content_count = len(content_list)
    if content_list is None or content_count == 0:
        print 'No files or folders found'
        sys.exit(2)

    os.nice(10)
    item_count = 0
    for item in content_list:
        item_folder = os.path.join(source_folder, item)
        if not os.path.isdir(item_folder):
            continue

        if len(item) > 70:
            print '{0:70}'.format(item[:70]),
        else:
            print '{0:70}'.format(item),

        print 'Checked'
        item_count += 1

    print "Processed %d movie(s)" % item_count


if __name__ == '__main__':
    main()
