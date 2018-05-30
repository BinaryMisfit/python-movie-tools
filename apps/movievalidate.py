#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE VALIDATOR UPDATER
# ###

# Check an MKV for valid video and audio tracks and then strips everything except the 2 valid
# tracks

# Current Version: 0.0.1
##########################################################################


def read_mkv_file(source_file):
    """Retrieve MKV file information"""
    import sys
    import collections
    import enzyme
    from enzyme.exceptions import MalformedMKVError
    result = collections.namedtuple('Result', 'mkv_file error')
    with open(source_file, 'rb') as mkv_source:
        try:
            mkv_file = enzyme.MKV(mkv_source)
        except MalformedMKVError:
            return result(None, '[ERROR] %s' % sys.exc_info()[0])

    return result(mkv_file, None)


def find_valid_video_track(media_file):
    """Check if the video tracks for the file contains a valid track"""
    if hasattr(media_file, 'video_tracks'):
        for video_track in media_file.video_tracks:
            if hasattr(video_track, 'language'):
                if video_track.language == 'English':
                    return video_track.number - 1

                if video_track.language == 'eng':
                    return video_track.number - 1

                if video_track.language == 'und':
                    return video_track.number - 1

                if video_track.language is None:
                    return video_track.number - 1

    return None


def find_valid_audio_track(media_file):
    """Check if the audio tracks for the file contains a valid track"""
    if hasattr(media_file, 'audio_tracks'):
        for audio_track in media_file.audio_tracks:
            if hasattr(audio_track, 'channels'):
                if audio_track.channels in [6, 8]:
                    if hasattr(audio_track, 'language'):
                        if audio_track.language == 'English':
                            return audio_track.number - 1

                        if audio_track.language == 'eng':
                            return audio_track.number - 1

                        if audio_track.language == 'und':
                            return audio_track.number - 1

                        if audio_track.language is None:
                            return audio_track.number - 1


def create_output_file(source_file, output_file, title_name, video_track, audio_track):
    """Generate a new MKV output file with only valid tracks"""
    import envoy
    import disklibrary
    mkv_executable = 'mkvmerge'
    mkv_installed = disklibrary.cmd_exists(mkv_executable)
    nice_executable = 'nice'
    nice_installed = disklibrary.cmd_exists(nice_executable)
    if not mkv_installed:
        return '[ERROR] Package mkvtoolnix not found'

    mkv_command = ''
    if nice_installed:
        mkv_command = 'nice -n 9 '

    mkv_command += 'mkvmerge -o \"' + output_file + '\" --title \"' + title_name + '\" --track-order 0:' \
                   + str(video_track) + ',0:' + str(audio_track) + ' --video-tracks ' + str(video_track) \
                   + ' --audio-tracks ' + \
        str(audio_track) + ' --no-subtitles --no-chapters \"' + source_file + '\"'
    output = envoy.run(mkv_command)
    if output.status_code != 0:
        return '[ERROR] Command output\n%s' % output.std_out

    return None


def validate_file(source_file):
    """Validate MKV file"""
    import os
    import disklibrary
    print 'Checking file %s' % source_file
    file_check = disklibrary.file_check(source_file, 'mkv')
    if file_check is None:
        print 'Not a valid MKV file %s' % source_file
        return 1

    os.nice(10)
    print 'Loading MKV file %s' % source_file
    source_file = disklibrary.file_split(source_file)
    print 'Processing file %s' % source_file.file_name
    source_mkv_file = read_mkv_file(source_file.full_path)
    if source_mkv_file.error is not None:
        print source_mkv_file.error
        return 2

    source_mkv_file = source_mkv_file.mkv_file
    print 'Checking video tracks'
    use_video_track = find_valid_video_track(source_mkv_file)
    print 'Checking audio tracks'
    use_audio_track = find_valid_audio_track(source_mkv_file)
    if use_video_track is None:
        print 'Selected MKV does not contain a valid video track'
        return 2

    if use_audio_track is None:
        if use_audio_track is None:
            print 'Selected MKV does not contain a valid audio track'
            return 2

    conversion_needed = len(source_mkv_file.video_tracks) != 1
    conversion_needed = conversion_needed or len(source_mkv_file.audio_tracks) != 1
    print conversion_needed
    if not conversion_needed:
        print 'File already in correct format'
        return 0

    final_link = source_file
    source_link = disklibrary.file_path(
        source_file.file_path, source_file.file_title + '.original')
    source_link = disklibrary.file_split(source_link)
    source_moved = disklibrary.file_rename(
        final_link.full_path, source_link.full_path)
    if not source_moved:
        print 'Could not create backup of %s' % final_link.file_name
        return 2

    check_file = disklibrary.file_check(final_link.full_path, 'mkv')
    if check_file is not None:
        disklibrary.file_delete(final_link)

    print 'Creating new file %s' % final_link.file_name
    error = create_output_file(source_link.full_path, final_link.full_path, final_link.file_title,
                               use_video_track, use_audio_track)
    if error is not None:
        print error
        return 2

    disklibrary.file_delete(source_link.full_path)
    print 'Created new file %s' % final_link.file_name
    return 0


def main():
    """Main script interface for Movie Validator"""
    import sys
    import argparse
    print 'Starting Movie Validate'
    parser = argparse.ArgumentParser(
        description='Checks a MKV file for valid video and audio tracks')
    parser.add_argument('file', metavar='file', type=str,
                        help='File to be checked')
    args = parser.parse_args()
    source_file = args.file
    output = validate_file(source_file)
    sys.exit(output)


if __name__ == '__main__':
    main()
