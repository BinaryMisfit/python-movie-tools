#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE PREPARATION SCRIPT
# ###

# Prepares movie for internal library addition

# Current Version: 0.0.1
##########################################################################


def movie_validate(source_file):
    """Validate the movie file"""
    import movievalidate
    output = movievalidate.validate_file(source_file)
    return output


def nfo_update(source_file):
    """Update the movie information"""
    import movienfo
    output = movienfo.generate_nfo(source_file, None, None)
    return output


def rename_movie(source_path):
    """Rename the movie and it's content"""
    import movierenamer
    output = movierenamer.rename_movie(source_path)
    return output


def target_folder(source_path):
    """Returns the final folder for the move output"""
    import movierenamer
    target_file = movierenamer.sorted_folder(source_path)
    return target_file


def notify_couchpotato(source_file):
    """Informing CouchPotato of the new file"""
    import moviecp
    output = moviecp.notify_couchpotato(source_file)
    return output


def process_mkv(source_file):
    """Process MKV file"""
    import sys
    import disklibrary
    print 'Processing Matroska Video File'
    print 'Validating %s' % source_file.file_name
    output = movie_validate(source_file.full_path)
    if output != 0:
        sys.exit(output)

    print 'Updating NFO for %s' % source_file.file_name
    output = nfo_update(source_file.full_path)
    if output != 0:
        sys.exit(output)

    output_file = target_folder(source_file.file_path)
    output = rename_movie(source_file.file_path)
    if output != 0:
        sys.exit(output)

    output = notify_couchpotato(output_file)
    if output != 0:
        sys.exit(output)

    return source_file


def main():
    """Main script interface for Movie Preparation Script"""
    import os
    import sys
    import argparse
    import disklibrary
    print 'Preparing movie'
    parser = argparse.ArgumentParser(
        description='Prepares movie for internal library addition')
    parser.add_argument('folder', metavar='folder', type=str,
                        help='Folder to be checked')
    args = parser.parse_args()
    source_folder = args.folder
    print 'Checking folder %s' % source_folder
    if not os.path.exists(source_folder):
        print 'Folder not found'
        sys.exit(0)

    source_file = disklibrary.file_first(source_folder, 'mkv')
    source_file = disklibrary.file_split(source_file)
    if source_file is None:
        print 'No valid file found for processing'
        sys.exit(0)

    if source_file.file_extension == '.mkv':
        source_file = process_mkv(source_file)

    print 'Completed processing %s' % source_file.file_title
    sys.exit(0)


if __name__ == '__main__':
    main()
