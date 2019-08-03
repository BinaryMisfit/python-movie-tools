#!/usr/bin/env python

##########################################################################
# SABnzb Movie Post Process
# ###

# Provides post processing for movies downloaded via SABnzb

# Current Version: 0.0.1
##########################################################################


class SABResult(object):
    def __init__(self, result, convert=False, data=None, error=None, video_track=0, audio_track=0):
        self.result = result
        self.data = data
        self.error = error
        self.convert = convert
        self.video_track = video_track
        self.audio_track = audio_track

    def __repr__(self):
        return '<SABResult result:%r data: %s error: %s convert: %r video_track: %s audio_track: %s>' \
            % (self.result, self.data, self.error, self.convert, self.video_track, self.audio_track)

    def __str__(self):
        return repr(self)


def check_valid_files(folder):
    """Check if a valid MKV file exists"""
    from lib_disk_util import check_contains_file
    list_files = check_contains_file(folder, '*.mkv')
    if not list_files.result:
        return SABResult(False, error=list_files.error)

    if list_files.data is None:
        return SABResult(False, error='No files to process')

    mkv_file = None
    check_file_size = 0
    for file in list_files.data:
        if (file.stat().st_size > check_file_size):
            check_file_size = file.stat().st_size
            if not mkv_file is None:
                mkv_file.unlink()

            mkv_file = file
        elif not mkv_file is None:
            file.unlink()

    if mkv_file is None:
        return SABResult(False, error='MKV file not found')

    return SABResult(True, data=mkv_file)


def validate_mkv_file(file):
    """Manage the conversion process for the MKV files"""
    if file is None:
        return SABResult(False, error='File not found')

    validate_success = read_mkv_file(str(file))
    if validate_success.result:
        validate_success = validate_conversion(validate_success.data)

    if validate_success.result:
        if not validate_success.convert:
            return SABResult(True, data=file, convert=False)

        return SABResult(True, data=file, convert=True, video_track=validate_success.video_track, audio_track=validate_success.audio_track)

    return SABResult(False, error=validate_success.error)


def read_mkv_file(file):
    """Retrieve MKV file information"""
    import sys
    import enzyme
    from enzyme.exceptions import MalformedMKVError
    with open(file, 'rb') as mkv_source:
        try:
            mkv_file = enzyme.MKV(mkv_source)
        except MalformedMKVError:
            return SABResult(False, error='[ERROR] %s' % sys.exc_info()[0])

    return SABResult(True, data=mkv_file)


def find_valid_video_track(file_data):
    """Check if the video tracks for the file contains a valid track"""
    if hasattr(file_data, 'video_tracks'):
        for video_track in file_data.video_tracks:
            print('Video Track: #%d' % video_track.number)
            if hasattr(video_track, 'language'):
                print('Video: %s' % video_track.language)
                if video_track.language == 'English':
                    return video_track.number - 1

                if video_track.language == 'eng':
                    return video_track.number - 1

                if video_track.language == 'und':
                    return video_track.number - 1

                if video_track.language is None:
                    return video_track.number - 1

    return None


def find_valid_audio_track(file_data):
    """Check if the audio tracks for the file contains a valid track"""
    if hasattr(file_data, 'audio_tracks'):
        for audio_track in file_data.audio_tracks:
            print('Audio Track: #%d' % audio_track.number)
            if hasattr(audio_track, 'channels'):
                print('Channels: %d' % audio_track.channels)
                if audio_track.channels in [6, 8]:
                    if hasattr(audio_track, 'language'):
                        print('Language: %s' % audio_track.language)
                        if audio_track.language == 'English':
                            return audio_track.number - 1

                        if audio_track.language == 'eng':
                            return audio_track.number - 1

                        if audio_track.language == 'und':
                            return audio_track.number - 1

                        if audio_track.language is None:
                            return audio_track.number - 1


def validate_conversion(file_data):
    """Validate the MKV file contains required tracks"""
    use_video_track = find_valid_video_track(file_data)
    use_audio_track = find_valid_audio_track(file_data)
    if use_video_track is None:
        return SABResult(False, error='No valid video track')

    if use_audio_track is None:
        if use_audio_track is None:
            return SABResult(False, error='No valid audio track')

    if int(use_video_track) == 0:
        return SABResult(False, error='No valid video track')

    if int(use_audio_track) == 0:
        return SABResult(False, error='No valid audio track')

    convert = len(file_data.video_tracks) != 1
    convert = convert or len(file_data.audio_tracks) != 1
    convert = convert or len(file_data.subtitle_tracks) > 0
    print('Validate MKV:\t\tConversion - %r' % convert)
    print('Validate MKV:\t\tVideo: {0} - Audio: {1}', use_video_track, use_audio_track)
    return SABResult(True, convert=True, video_track=use_video_track, audio_track=use_audio_track)


def convert_mkv_file(folder, file, video_track, audio_track):
    """Convert the MKV file if required"""
    convert_success = backup_original_file(folder, file)
    if convert_success.result:
        return create_output_file(convert_success.data, file, video_track, audio_track)

    return SABResult(False, error=convert_success.error)


def backup_original_file(folder, file):
    """Backup the original MKV file"""
    from pathlib import Path
    from lib_disk_util import rename_file, file_size_format
    backup_name = '%s%s' % (file.name, '.original')
    backup_folder = Path(folder)
    backup_file = backup_folder.joinpath(backup_name)
    backup_success = rename_file(str(file), str(backup_file))
    if backup_success.result:
        backup_file = Path(backup_success.data)
        if backup_file.exists():
            source_size = file_size_format(backup_file.stat().st_size)
            print('Convert MKV:\t\tFile size - %s' % source_size)
            return SABResult(True, data=str(backup_file))

    return SABResult(False, error=backup_success.error)


def create_output_file(source_file, output_file, video_track, audio_track):
    """Generate a new MKV output file with only valid tracks"""
    from delegator import run
    from lib_disk_util import cmd_exists, delete_file
    executable = '/usr/local/bin/mkvmerge'
    installed = cmd_exists(executable)
    if not installed:
        return SABResult(False, error='Package mkvtoolnix not found')

    command = '%s -o \"%s\" --track-order 0:%s,0:%s --video-tracks %s --audio-tracks %s ' \
              '--no-subtitles --no-chapters \"%s\"' \
        % (executable, output_file, video_track, audio_track, video_track, audio_track, source_file)
    output = run(command)
    result_code = output.return_code
    result_content = output.out
    if int(result_code) == 0:
        delete_file(source_file)
        return SABResult(True, data=output_file)

    return SABResult(False, error='Command output\n%s' % result_content)


def main():
    """Main script interface for SABnzb Movie Post Process"""
    import sys
    import os
    sab_category = os.environ['SAB_CAT']
    sab_directory = os.environ['SAB_COMPLETE_DIR']
    sab_pp_status = os.environ['SAB_PP_STATUS']
    if not sab_category == 'movies':
        print('Skipping - Not in movies category')
        sys.exit(0)
    if not sab_directory.strip():
        print('Skipping - Directory not supplied')
        sys.exit(0)
    if not int(sab_pp_status) == 0:
        print('Skipping - Post processing failed with status %s' % sab_pp_status)
        sys.exit(0)

    """Validate files exists and can be processed"""
    validate_files_result = check_valid_files(sab_directory)
    script_success = validate_files_result
    if validate_files_result.result:
        print('Validate Files:\t\tSuccess')
    else:
        print('Validate Files:\t\tFailed')

    """Check a valid MKV source exists"""
    mkv_source = None
    if validate_files_result.result:
        mkv_source = validate_files_result.data
        validate_mkv_result = validate_mkv_file(mkv_source)
        script_success = validate_mkv_result
        if validate_mkv_result.result:
            print('Validate MKV:\t\tSuccess')
        else:
            print('Validate MKV:\t\tFailed')
    else:
       print('Validate MKV:\t\tFailed')

    """Convert MKV if required"""
    if validate_mkv_result.result:
        if validate_mkv_result.convert:
            convert_result = convert_mkv_file(
                sab_directory, validate_mkv_result.data, validate_mkv_result.video_track, validate_files_result.audio_track)
            script_success = convert_result
            if convert_result.result:
                print('Convert MKV:\t\tSuccess')
            else:
                print('Convert MKV:\t\tFailed')
        else:
            print('Convert MKV:\t\tSkipped')
    else:
       print('Convert MKV:\t\tFailed')

    """Handle script result and completion"""
    if script_success.result:
        sys.exit(0)

    if script_success.error is None:
        sys.exit(1)

    print('Failed:\t\t\t%s' % script_success.error)
    sys.exit(1)


if __name__ == '__main__':
    main()
