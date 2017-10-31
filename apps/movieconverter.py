#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE CONVERTER
# ###

# Converts a MKV file to a valid M4V file

# Current Version: 0.0.1
##########################################################################


def create_output_file(source_file, destination_file):
    """Create the M4V file"""
    import disklibrary
    import envoy
    ffmpeg_executable = 'ffmpeg'
    ffmpeg_installed = disklibrary.cmd_exists(ffmpeg_executable)
    nice_executable = 'nice'
    nice_installed = disklibrary.cmd_exists(nice_executable)
    if not ffmpeg_installed:
        return '[ERROR] Package ffmpeg not found'

    ffmpeg_command = ''
    if nice_installed:
        ffmpeg_command = 'nice -n 9 '

    ffmpeg_command += 'ffmpeg -i \"' + source_file + '\" -strict experimental ' \
        '-map 0:0 -map 0:1 -map 0:1 -c:v copy ' \
        '-c:a:0 aac -ac:a:0 2 -b:a:0 160k -c:a:1 ac3 -ac:a:1 6 -b:a:1 384k -v error ' \
        '\"' + destination_file + '\"'
    output = envoy.run(ffmpeg_command)
    if output.status_code != 0:
        return '[ERROR] Command output\n%s' % output.std_err

    return None


def movie_convert(source_file):
    """Convert the MKV file to valid M4V file"""
    import os
    import disklibrary
    print 'Checking file %s' % source_file
    file_check = disklibrary.file_check(source_file, 'mkv')
    if file_check is None:
        print 'Not a valid MKV file %s' % source_file
        return 1

    os.nice(10)
    source_link = disklibrary.file_split(source_file)
    print 'Processing file %s' % source_link.file_name
    final_link = disklibrary.file_path(
        source_link.file_path, source_link.file_title + '.m4v')
    if disklibrary.file_check(final_link, 'm4v') is not None:
        disklibrary.file_delete(final_link)

    final_link = disklibrary.file_split(final_link)
    print 'Creating new file %s' % final_link.file_name
    error = create_output_file(source_link.full_path, final_link.full_path)
    if error is not None:
        print error
        return 2

    print 'Removing source file'
    disklibrary.file_delete(source_link.full_path)
    return 0


def main():
    """Converts a MKV file to a valid M4V file"""
    import sys
    import argparse
    print 'Starting Movie Convert'
    parser = argparse.ArgumentParser(description='Convert MKV to M4V file')
    parser.add_argument('file', metavar='file', type=str,
                        help='File to be converted')
    args = parser.parse_args()
    source_file = args.file
    output = movie_convert(source_file)
    sys.exit(output)


if __name__ == '__main__':
    main()
