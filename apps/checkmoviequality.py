##########################################################################
# MOVIE QUALITY CHECK
# ###

# Checks an MKV for it's current video quality

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


def get_media_info(source_file):
    from pymediainfo import MediaInfo
    media_info = MediaInfo.parse(source_file)
    return media_info;

def get_video_quality(media_info):
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
    return return_quality

def main():
    """Main script interface for Movie Quality Check"""
    import sys
    import argparse
    print 'Starting Movie Quality Check'
    parser = argparse.ArgumentParser(
        description='Checks a MKV file for video quality')
    parser.add_argument('file', metavar='file', type=str,
                        help='File to be checked')
    args = parser.parse_args()
    source_file = args.file
    detail = get_media_info(source_file)
    quality = get_video_quality(detail)
    print "Movie quality is " + quality
    if "Unknown" not in quality:
        sys.exit(0)
    sys.exit(1)


if __name__ == '__main__':
    main()
