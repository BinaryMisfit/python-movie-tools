#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE ORGANISER
# ###

# Check a list of folders for movies and provides the correct information for these movies
#
# Current Version: 0.0.1
##########################################################################


def movie_update(file_path):
    """Output movie"""
    import os
    import envoy
    movie_update_path = os.path.realpath(__file__)
    movie_update_path = os.path.dirname(movie_update_path)
    movie_update_path = os.path.join(movie_update_path, 'movieupdater.py')
    movie_update_path += ' \"' + file_path + '\"'
    output = envoy.run(movie_update_path)
    if output.status_code != 0:
        return output.std_out

    return None


def movie_nfo_create(file_path):
    """Create movie NFO"""
    import os
    import envoy
    movie_nfo_create_path = os.path.realpath(__file__)
    movie_nfo_create_path = os.path.dirname(movie_nfo_create_path)
    movie_nfo_create_path = os.path.join(
        movie_nfo_create_path, 'nfocreator.py')
    movie_nfo_create_path += ' \"' + file_path + '\"'
    output = envoy.run(movie_nfo_create_path)
    if output.status_code != 0:
        return output.std_out

    return None


def movie_rename(file_path):
    """Rename movie"""
    import os
    import envoy
    movie_renamer_path = os.path.realpath(__file__)
    movie_renamer_path = os.path.dirname(movie_renamer_path)
    movie_renamer_path = os.path.join(movie_renamer_path, 'movierenamer.py')
    movie_renamer_path += ' \"' + file_path + '\"'
    output = envoy.run(movie_renamer_path)
    if output.status_code != 0:
        return output.std_out

    return None


def main():
    """Entry point for movie organiser script"""
    import os
    import sys
    import argparse
    import disklibrary
    print 'Starting Movie Organiser'
    parser = argparse.ArgumentParser(
        description="Organise all movies found inside a folder")
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
    print 'Processing folder %s' % source_folder
    item_count = 0
    total_count = 0
    for item in content_list:
        item_folder = os.path.join(source_folder, item)
        if not os.path.isdir(item_folder):
            continue

        total_count += 1
        if len(item) > 70:
            print '{0:70}'.format(item[:70]),
        else:
            print '{0:70}'.format(item),

        print 'MKV:',
        movie_file = disklibrary.file_first(item_folder, 'mkv')
        if movie_file is None:
            print '{0:15}'.format('Not found'),
            continue

        print '{0:15}'.format('Found'),
        print '\tNFO:',
        nfo_file = disklibrary.file_first(item_folder, 'nfo')
        if nfo_file is not None:
            print '{0:15}'.format('Found')
            continue

        print '{0:15}'.format('Not found'),
        item_count += 1
        print '\tFile:',
        print '{0:10}'.format(item_count),
        movie_file = os.path.join(item_folder, movie_file)
        print '\tTMDB:',
        output = movie_update(movie_file)
        if output is not None:
            print '%s error:\n%s' % (item, output)
            sys.exit(2)

        print '{0:15}'.format('Complete'),
        print '\tNFO:',
        output = movie_nfo_create(movie_file)
        if output is not None:
            print '%s error:\n%s' % (item, output)
            sys.exit(2)

        print '{0:10}'.format('Complete'),
        print '\tRename:',
        output = movie_rename(movie_file)
        if output is not None:
            print '%s error:\n%s' % (item, output)
            sys.exit(2)

        print '{0:15}'.format('Complete')

    sys.exit(0)


if __name__ == "__main__":
    main()
