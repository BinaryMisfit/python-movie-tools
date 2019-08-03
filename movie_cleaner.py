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

    def __init__(self, mkv_file, orignal_name=None, new_name=None, folder_name=None,
                 parent=None, quality=None, needs_clean=False, new_parent=False,
                 needs_quality=False, result='', error=False):
        self.mkv_file = mkv_file
        self.orignal_name = orignal_name
        self.folder_name = folder_name
        self.new_name = new_name
        self.parent = parent
        self.quality = quality
        self.needs_clean = needs_clean
        self.new_parent = new_parent
        self.needs_quality = needs_quality
        self.result = result
        self.error = error

    def __repr__(self):
        return '<MovieFolder mkv_file: %s, orignal_name: %s, new_name: %s, folder_name: %s, ' \
            'parent: %s, needs_clean: %r, new_parent: %r, needs_quality: %r, result: %s, ' \
            ' error: %r>' % (self.mkv_file, self.folder_name, self.orignal_name, self.new_name,
                             self.parent, self.needs_clean, self.new_parent, self.needs_quality,
                             self.result, self.error)

    def __str__(self):
        return repr(self)


def clean_movie_folder(movie_folder):
    clean_folder = Path(movie_folder.parent)
    clean_files = []
    clean_files.extend(clean_folder.glob('*.jpg'))
    clean_files.extend(clean_folder.glob('*.nfo'))
    clean_files.extend(clean_folder.glob('*.srt'))
    for clean_file in clean_files:
        clean_file.unlink()

    movie_folder.needs_clean = False
    return movie_folder


def get_video_quality(movie_folder):
    from pymediainfo import MediaInfo
    from lib_disk_util import file_size_format
    movie_size = movie_folder.mkv_file.stat().st_size / 10 * 30
    print(movie_folder.mkv_file.stat().st_size)
    print(movie_size)
    print(file_size_format(movie_folder.mkv_file.stat().st_size))
    media_info = MediaInfo.parse(movie_folder.mkv_file)
    return_quality = "Unknown"
    for track in media_info.tracks:
        if track.track_type == "Video":
            print "Width: " + track.sampled_width
            print "Height: " + track.sampled_height
            if int(track.sampled_width) == 1920:
                print "Format: 1080p"
                return_quality = "1080p"
            elif int(track.sampled_width) == 1280:
                print "Format: 720p"
                return_quality = "720p"
            if int(track.sampled_height) >= 1000:
                print "Type: Bluray"
                return_quality = "Bluray-" + return_quality
            elif int(track.sampled_height) >= 800:
                print "Type: HDTV"
                return_quality = "HDTV-" + return_quality
            elif int(track.sampled_height) >= 500:
                print "Type: Bluray"
                return_quality = "Bluray-" + return_quality
            else:
                print "Type: HDTV"
                return_quality = "HDTV-" + return_quality
    movie_folder.quality = return_quality
    return movie_folder


def add_quality(movie_folder):
    movie_folder = get_video_quality(movie_folder)
    movie_folder.new_name = '%s %s.%s' % (
        movie_folder.mkv_file.name, movie_folder.quality, movie_folder.mkv_file.suffix)
    movie_folder.needs_quality = False
    return movie_folder


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

    movie_folder.orignal_name = mkv_file.name
    movie_folder.folder_name = mkv_file.parent.name
    movie_folder.parent = mkv_file.parent
    mkv_parent = Path(movie_folder.parent)
    list_files = []
    list_files.extend(mkv_parent.glob('*.jpg'))
    list_files.extend(mkv_parent.glob('*.nfo'))
    list_files.extend(mkv_parent.glob('*.srt'))
    needs_clean = len(list_files) > 0
    movie_folder.needs_clean = needs_clean
    movie_folder.new_parent = not mkv_file.name == movie_folder.folder_name
    movie_folder.needs_quality = not '[' in mkv_file.name and not ']' in mkv_file.name
    return movie_folder


def main():
    """Main entry point for script"""
    from colorama import init
    from termcolor import colored
    import sys
    import argparse
    init()
    print 'Starting Movie Renamer'
    parser = argparse.ArgumentParser(
        description='Clean a MKV file name and all relevant files and tags')
    parser.add_argument('file', metavar='file', type=str,
                        help='MKV file to clean')
    args = parser.parse_args()
    print('MKV File\t\t%s' % args.file)
    movie = validate_mkv(args.file)
    if movie.error:
        print('Validation:\t\t%s%s' %
              colored('Failed - ', 'red'), colored(movie.result, 'red'))
    else:
        print('Validation:\t\t%s' % colored('Success', 'green'))

    if movie.needs_clean:
        if not movie.error:
            movie = clean_movie_folder(movie)
            if movie.error:
                print('Cleanup:\t\t%s%s' %
                      colored('Failed - ', 'red'), colored(movie.result, 'red'))
            else:
                print('Cleanup:\t\t%s' % colored('Success', 'green'))
    else:
        print('Cleanup:\t\t%s' % colored('Skipped', 'yellow'))

    if movie.needs_quality:
        if not movie.error:
            movie = add_quality(movie)
            if movie.error:
                print('Quality:\t\t%s%s' %
                      colored('Failed - ', 'red'), colored(movie.result, 'red'))
            else:
                print('Qaulity:\t\t%s' % colored('Success', 'green'))
    else:
        print('Quality:\t\t%s' % colored('Skipped', 'yellow'))

    print(movie)
    if movie.error:
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
