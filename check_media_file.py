#!/usr/bin/env python2
###
# A supplied file will be checked for media type and valid video and launguage # information.
###


def prepare_args():
    import argparse
    parser = argparse.ArgumentParser(
        description="Check media file information")
    parser.add_argument(
        "filename", help="The name of the file to be checked")
    args = parser.parse_args()
    print(args.filename)


def main():
    import sys
    prepare_args()
    sys.exit(0)


if __name__ == "__main__":
    main()
