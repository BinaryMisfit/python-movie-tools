#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE INFO MISSING FINDER
# ###

# Check a list of folders for movies and provides the correct information for these movies
#
# Current Version: 0.0.1
##########################################################################


def main():
    """Missing movie info finder"""
    import os
    import sys
    import argparse
    import disklibrary
    print 'Starting Movie Info Missing Finder'
    parser = argparse.ArgumentParser(
        description='Checks for missing movie information')
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

        try:
            m4v_file = disklibrary.file_first(item_folder, 'm4v')
            m4v_file = disklibrary.file_split(m4v_file)

            nfo_found = False
            nfo_file = disklibrary.file_first(item_folder, 'nfo')
            if nfo_file:
                nfo_file = disklibrary.file_split(nfo_file)
                nfo_found = m4v_file.file_title == nfo_file.file_title

            cover_found = False
            cover_file = '%s/%s-cover.jpg' % (m4v_file.file_path,
                                              m4v_file.file_title)
            cover_file = disklibrary.file_check(cover_file, 'jpg')
            if cover_file:
                cover_found = True

            poster_found = False
            poster_file = '%s/%s-fanart.jpg' % (
                m4v_file.file_path, m4v_file.file_title)
            poster_file = disklibrary.file_check(poster_file, 'jpg')
            if poster_file:
                poster_found = True

            if not nfo_found or not cover_file or not poster_file:
                if len(m4v_file.file_title) > 70:
                    print '{0:70}'.format(m4v_file.file_title[:70]),
                else:
                    print '{0:70}'.format(m4v_file.file_title),

                print('NFO:'),
                if nfo_found:
                    print '{0:15}'.format('Found'),
                else:
                    print '{0:15}'.format('Not found'),

                print('\tCover:'),
                if cover_found:
                    print '{0:15}'.format('Found'),
                else:
                    print '{0:15}'.format('Not found'),

                print('\tPoster:'),
                if poster_found:
                    print '{0:15}'.format('Found')
                else:
                    print '{0:15}'.format('Not found')

                item_count += 1

        except Exception as exception:
            print '%s error: %s' % (item_folder, exception.message)
            break

    print 'Missing NFO files: %d' % item_count
    sys.exit(0)


if __name__ == '__main__':
    main()
