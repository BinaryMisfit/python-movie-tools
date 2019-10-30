#!/usr/bin/env python2
###
# A supplied file will be checked for media type and valid video and language
# information.
###


class MediaFile(object):
    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        return ("<MediaFile filename: {0}").format(self.filename)

    def __str__(self):
        return repr(self)


def prepare_args():
    import argparse
    parser = argparse.ArgumentParser(
        description="Check media file information")
    parser.add_argument(
        "filename", help="The name of the file to be checked")
    args = parser.parse_args()
    media_file = MediaFile(filename=args.filename)
    print(media_file)


def main():
    from sys import exit
    prepare_args()
    exit(0)


if __name__ == "__main__":
    main()
