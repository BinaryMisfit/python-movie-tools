#!/usr/bin/env python

##########################################################################
# SABnzb Movie Post Process
# ###

# Provides post processing for movies downloaded via SABnzb

# Current Version: 0.0.1
##########################################################################


class SABResult(object):
    def __init__(self,
                 result,
                 convert=False,
                 data=None,
                 encode=False,
                 error=None,
                 video_track=0,
                 audio_track=0):
        self.result = result
        self.data = data
        self.encode = encode
        self.error = error
        self.convert = convert
        self.video_track = video_track
        self.audio_track = audio_track

    def __repr__(self):
        return ("<SABResult result: {0} data: {1} error: {2} convert: {3} "
                "encode: {4}, video_track: {5} audio_track: {6}>").format(
                    self.result, self.data, self.error, self.convert,
                    self.encode, self.video_track, self.audio_track)

    def __str__(self):
        return repr(self)


def check_valid_files(folder):
    """Check if a valid MKV file exists"""
    from lib_disk_util import check_contains_file
    encode = False
    print("Check MKV")
    list_files = check_contains_file(folder, "*.mkv")
    print(list_files)
    if not list_files.result:
        print("Check MP4")
        list_files = check_contains_file(folder, "*.mp4")
        encode = True

    media_files = list_files.data
    print(media_files)
    if not list_files.result:
        return SABResult(False, error=list_files.error)

    if len(media_files) == 0:
        return SABResult(False, error="No files to process")

    media_file = None
    check_file_size = 0
    for list_file in media_files:
        if (list_file.stat().st_size > check_file_size):
            check_file_size = list_file.stat().st_size
            if media_file is not None:
                media_file.unlink()

            media_file = list_file
        elif media_file is not None:
            list_file.unlink()

    print(("Media File: {0}").format(media_file))
    if media_file is None:
        return SABResult(False, error="Media file not found")

    return SABResult(True, encode=encode, data=media_file)


def read_mkv_file(source_file):
    """Retrieve MKV file information"""
    import sys
    import enzyme
    from enzyme.exceptions import MalformedMKVError
    with open(source_file, "rb") as mkv_source:
        try:
            mkv_file = enzyme.MKV(mkv_source)
        except MalformedMKVError:
            return SABResult(False,
                             error="[ERROR] {0}".format(sys.exc_info()[0]))

    return SABResult(True, data=mkv_file)


def find_valid_video_track(file_data):
    """Check if the video tracks for the file contains a valid track"""
    if hasattr(file_data, "video_tracks"):
        for video_track in file_data.video_tracks:
            if hasattr(video_track, "language"):
                if video_track.language == "English":
                    return video_track.number - 1

                if video_track.language == "eng":
                    return video_track.number - 1

                if video_track.language == "und":
                    return video_track.number - 1

                if video_track.language is None:
                    return video_track.number - 1

    return None


def find_valid_audio_track(file_data):
    """Check if the audio tracks for the file contains a valid track"""
    if hasattr(file_data, "audio_tracks"):
        for audio_track in file_data.audio_tracks:
            if hasattr(audio_track, "channels"):
                if audio_track.channels in [6, 8]:
                    if hasattr(audio_track, "language"):
                        if audio_track.language == "English":
                            return audio_track.number - 1

                        if audio_track.language == "eng":
                            return audio_track.number - 1

                        if audio_track.language == "und":
                            return audio_track.number - 1

                        if audio_track.language is None:
                            return audio_track.number - 1


def validate_conversion(convert_file):
    """Validate the MKV file contains required tracks"""
    mkv_file = read_mkv_file(str(convert_file))
    if not mkv_file.result:
        return SABResult(False, error="Error reading MKV file")

    file_data = mkv_file.data
    use_video_track = find_valid_video_track(file_data)
    use_audio_track = find_valid_audio_track(file_data)
    if use_video_track is None:
        return SABResult(False, error="No valid video track")

    if use_audio_track is None:
        if use_audio_track is None:
            return SABResult(False, error="No valid audio track")

    convert = len(file_data.video_tracks) != 1
    convert = convert or len(file_data.audio_tracks) != 1
    convert = convert or len(file_data.subtitle_tracks) > 0
    print("Validate MKV:\t\tConversion - {0}".format(convert))
    return SABResult(True,
                     convert=True,
                     video_track=use_video_track,
                     audio_track=use_audio_track)


def validate_mkv_file(validate_file):
    """Manage the conversion process for the MKV files"""
    if validate_file is None:
        return SABResult(False, error="File not found")

    validate_success = validate_conversion(str(validate_file))
    if validate_success.result:
        if not validate_success.convert:
            return SABResult(True, data=validate_file, convert=False)

        return SABResult(True,
                         data=validate_file,
                         convert=True,
                         video_track=validate_success.video_track,
                         audio_track=validate_success.audio_track)

    return SABResult(False, error=validate_success.error)


def backup_original_file(folder, org_file):
    """Backup the original MKV file"""
    from pathlib import Path
    from lib_disk_util import rename_file, file_size_format
    backup_name = "{0}{1}".format(org_file.name, ".original")
    backup_folder = Path(folder)
    backup_file = backup_folder.joinpath(backup_name)
    backup_success = rename_file(str(org_file), str(backup_file))
    if backup_success.result:
        backup_file = Path(backup_success.data)
        if backup_file.exists():
            source_size = file_size_format(backup_file.stat().st_size)
            print("Convert MKV:\t\tFile size - {0}".format(source_size))
            return SABResult(True, data=str(backup_file))

        return SABResult(False, error=backup_success.error)


def create_output_file(source_file, output_file, video_track, audio_track):
    """Generate a new MKV output file with only valid tracks"""
    from delegator import run
    from lib_disk_util import cmd_exists, delete_file
    executable = "/usr/local/bin/mkvmerge"
    installed = cmd_exists(executable)
    if not installed:
        return SABResult(False, error="Package mkvtoolnix not found")

    command = ("{0} -o \"{1}\" --track-order 0:{2},0:{3} --video-tracks {2} "
               "--audio-tracks {3} --no-subtitles --no-chapters "
               "\"{4}\"").format(executable, output_file, video_track,
                                 audio_track, source_file)
    output = run(command)
    result_code = output.return_code
    result_content = output.out
    if int(result_code) == 0:
        delete_file(source_file)
        return SABResult(True, data=output_file)

    return SABResult(False, error="Command output\n{0}".format(result_content))


def convert_mp4_file(mp4_file):
    from delegator import run
    from lib_disk_util import cmd_exists, delete_file
    from pathlib import Path
    """Convert MP4 file to MKV"""
    mp4_file = Path(mp4_file)
    mkv_file = ("{0}.mkv").format(mp4_file.stem)
    print(("MP4 File: {0}").format(mp4_file))
    print(("MKV File: {0}").format(mkv_file))
    executable = "/usr/local/bin/ffmpeg"
    installed = cmd_exists(executable)
    if not installed:
        return SABResult(False, error="Package ffmpeg not found")

    command = ("{0} -i \"{1}\" -vcodec copy -acodec copy \"{2}\"").format(
        executable, mp4_file, mkv_file)
    print(command)
    output = run(command)
    result_code = output.return_code
    result_content = output.out
    if int(result_code) == 0:
        delete_file(mp4_file)
        return SABResult(True, data=mkv_file)

    return SABResult(False, error="Command output\n{0}".format(result_content))


def validate_output_file(source_file):
    """Validate the MKV file contains required tracks"""
    mkv_file = read_mkv_file(str(source_file))
    if not mkv_file.result:
        return SABResult(False, error="Error reading MKV file")

    file_data = mkv_file.data
    use_video_track = find_valid_video_track(file_data)
    use_audio_track = find_valid_audio_track(file_data)
    if use_video_track is None:
        return SABResult(False, error="No valid video track")

    if use_audio_track is None:
        if use_audio_track is None:
            return SABResult(False, error="No valid audio track")

    valid = len(file_data.video_tracks) == 1
    valid = valid or len(file_data.audio_tracks) == 1
    valid = valid or len(file_data.subtitle_tracks) == 0
    if valid:
        return SABResult(True, data=source_file)

    return SABResult(False, error="Broken conversion")


def convert_mkv_file(folder, mkv_file, video_track, audio_track):
    """Convert the MKV file if required"""
    convert_success = backup_original_file(folder, mkv_file)
    if convert_success.result:
        convert_success = create_output_file(convert_success.data, mkv_file,
                                             video_track, audio_track)

    if convert_success.result:
        convert_success = validate_output_file(convert_success.data)

    return convert_success


def main():
    """Main script interface for SABnzb Movie Post Process"""
    import sys
    import os
    sab_category = os.environ["SAB_CAT"]
    sab_directory = os.environ["SAB_COMPLETE_DIR"]
    sab_pp_status = os.environ["SAB_PP_STATUS"]
    if not sab_category == "movies":
        print("Skipping - Not in movies category")
        sys.exit(0)

    if not sab_directory.strip():
        print("Skipping - Directory not supplied")
        sys.exit(0)

    if not int(sab_pp_status) == 0:
        print("Skipping - Post processing failed "
              "with status {0}".format(sab_pp_status))
        sys.exit(0)

    validate_files_result = check_valid_files(sab_directory)
    script_success = validate_files_result
    if script_success.result:
        print("Validate Files:\t\tSuccess")
    else:
        print("Validate Files:\t\tFailed")

    media_source = None
    if script_success.result:
        if script_success.encode:
            media_source = script_success.data
            convert_mp4_result = convert_mp4_file(media_source)
            script_success = convert_mp4_result
            if script_success.result:
                print("Convert MP4:\t\tSuccess")
            else:
                print("Convert MP4:\t\tFailed")
        else:
            print("Convert MP4:\t\tSkipped")
    else:
        print("Convert MP4:\t\tFailed")

    if script_success.result:
        media_source = script_success.data
        validate_mkv_result = validate_mkv_file(media_source)
        script_success = validate_mkv_result
        if script_success.result:
            print("Validate MKV:\t\tSuccess")
        else:
            print("Validate MKV:\t\tFailed")
    else:
        print("Validate MKV:\t\tFailed")

    if script_success.result:
        if script_success.convert:
            convert_result = convert_mkv_file(sab_directory,
                                              validate_mkv_result.data,
                                              validate_mkv_result.video_track,
                                              validate_mkv_result.audio_track)
            script_success = convert_result
            if script_success.result:
                print("Convert MKV:\t\tSuccess")
            else:
                print("Convert MKV:\t\tFailed")
        else:
            print("Convert MKV:\t\tSkipped")
    else:
        print("Convert MKV:\t\tFailed")

    if script_success.result:
        sys.exit(0)

    if script_success.error is None:
        sys.exit(1)

    print("Failed:\t\t\t{0}".format(script_success.error))
    sys.exit(1)


if __name__ == "__main__":
    main()
