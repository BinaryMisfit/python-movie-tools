#!/usr/bin/env python3

##########################################################################
# Movie Cleaner
# ###

# Script to clean movie files and folders

# Current Version: 0.0.1
##########################################################################
from pathlib import Path


class MovieFolder(object):
    """Object containing all information for the script"""

    def __init__(self,
                 mkv_file,
                 org_name=None,
                 new_name=None,
                 folder_name=None,
                 parent=None,
                 quality=None,
                 needs_clean=False,
                 new_parent=False,
                 needs_quality=False,
                 result="",
                 error=False):
        self.mkv_file = mkv_file
        self.org_name = org_name
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
        return f"<MovieFolder mvk_file: {self.mkv_file}, org_name: "
        f"{self.org_name}, new_name: {self.new_name}, folder_name: "
        f"{self.folder_name}, parent: {self.parent}, needs_clean: "
        f"{self.needs_clean}, new_parent: {self.new_parent}, "
        f"needs_quality: {self.needs_quality} "
        f"result: {self.result}, error: {self.error}"

    def __str__(self):
        return repr(self)


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

    if not mkv_file.suffix == ".mkv":
        movie_folder.result = "Failed - Not a MKV file"
        movie_folder.error = True
        return movie_folder

    movie_folder.org_name = mkv_file.stem
    movie_folder.folder_name = mkv_file.parent.name
    movie_folder.parent = mkv_file.parent
    movie_folder = get_video_quality(movie_folder)
    mkv_parent = Path(movie_folder.parent)
    list_files = []
    list_files.extend(mkv_parent.glob("*.jpg"))
    list_files.extend(mkv_parent.glob("*.nfo"))
    list_files.extend(mkv_parent.glob("*.srt"))
    needs_clean = len(list_files) > 0
    movie_folder.needs_clean = needs_clean
    has_quality = ("[" in movie_folder.folder_name
                   and "]" in movie_folder.folder_name)
    match_name = not mkv_file.name.startswith(movie_folder.folder_name)
    movie_folder.new_parent = has_quality or match_name
    needs_quality = movie_folder.quality not in mkv_file.name
    movie_folder.needs_quality = needs_quality
    return movie_folder


def clean_movie_folder(movie_folder):
    clean_folder = Path(movie_folder.parent)
    clean_files = []
    clean_files.extend(clean_folder.glob("*.jpg"))
    clean_files.extend(clean_folder.glob("*.nfo"))
    clean_files.extend(clean_folder.glob("*.srt"))
    for clean_file in clean_files:
        clean_file.unlink()

    movie_folder.needs_clean = False
    return movie_folder


def get_video_quality(movie_folder):
    from pymediainfo import MediaInfo
    media_info = MediaInfo.parse(movie_folder.mkv_file)
    return_quality = None
    for track in media_info.tracks:
        if track.track_type == "Video":
            if int(track.sampled_width) == 1920:
                return_quality = "1080p"
                if int(track.sampled_height) >= 800:
                    return_quality = "Bluray-" + return_quality
                else:
                    return_quality = "HDTV-" + return_quality
            elif int(track.sampled_width) == 1280:
                return_quality = "720p"
                if int(track.sampled_height) >= 500:
                    return_quality = "Bluray-" + return_quality
            elif int(track.sampled_height) == 1080:
                return_quality = "Bluray-1080p"
            elif int(track.sampled_width) >= 1000:
                if int(track.sampled_height) >= 800:
                    return_quality = "Bluray-1080p"
    movie_folder.quality = return_quality
    return movie_folder


def add_quality(movie_folder):
    import sys
    movie_folder = get_video_quality(movie_folder)
    if movie_folder.quality is None:
        movie_folder.error = True
        movie_folder.result = "Unknown Movie Quality"
        return movie_folder

    movie_name = movie_folder.mkv_file.stem
    has_quality = "[" in movie_name and "]" in movie_name
    if has_quality:
        movie_name = movie_name[0:movie_name.index("[") - 1].strip()

    movie_folder.new_name = "{0} [{1}]{2}".format(movie_name,
                                                  movie_folder.quality,
                                                  movie_folder.mkv_file.suffix)
    movie_update = Path(movie_folder.parent)
    movie_update = movie_update.joinpath(movie_folder.new_name)
    try:
        movie_folder.mkv_file.rename(movie_update)
        movie_folder.mkv_file = movie_update
        movie_folder.needs_quality = False
    except IOError:
        movie_folder.error = True
        movie_folder.result = sys.exc_info()[0]

    return movie_folder


def rename_parent(movie_folder):
    import sys
    movie_name = movie_folder.org_name
    has_quality = "[" in movie_name and "]" in movie_name
    if has_quality:
        movie_name = movie_name[0:movie_name.index("[") - 1].strip()

    movie_rename = Path(movie_folder.parent)
    movie_update = movie_rename.parent
    movie_update = movie_update.joinpath(movie_name)
    try:
        movie_rename.rename(movie_update)
        movie_folder.parent = movie_update
        movie_folder.new_parent = False
    except IOError:
        movie_folder.error = True
        movie_folder.result = sys.exc_info()[0]

    return movie_folder


def process_folder(folder):
    from termcolor import colored
    print("MKV File\t\t{0}".format(folder))
    movie = validate_mkv(folder)
    if movie.quality is not None:
        print("Quality:\t\t{0}".format(movie.quality))
    if movie.error:
        print("Validation:\t\t{0}{1}".format(colored("Failed - ", "red"),
                                             colored(movie.result, "red")))
    else:
        print("Validation:\t\t{0}".format(colored("Success", "green")))

    if movie.needs_clean:
        if not movie.error:
            movie = clean_movie_folder(movie)
            if movie.error:
                print("Cleanup:\t\t{0}{1}".format(colored("Failed - ", "red"),
                                                  colored(movie.result,
                                                          "red")))
            else:
                print("Cleanup:\t\t{0}".format(colored("Success", "green")))
    else:
        print("Cleanup:\t\t{0}".format(colored("Skipped", "yellow")))

    if movie.needs_quality:
        if not movie.error:
            movie = add_quality(movie)
            if movie.error:
                print("Quality:\t\t{0}{1}".format(colored("Failed - ", "red"),
                                                  colored(movie.result,
                                                          "red")))
            else:
                print("Quality:\t\t{0}".format(colored("Success", "green")))
    else:
        print("Quality:\t\t{0}".format(colored("Skipped", "yellow")))

    if movie.new_parent:
        if not movie.error:
            movie = rename_parent(movie)
            if movie.error:
                print("Rename:\t\t\t{0}{1}".format(
                    colored("Failed - ", "red"), colored(movie.result, "red")))
            else:
                print("Rename:\t\t\t{0}".format(colored("Success", "green")))
    else:
        print("Rename:\t\t\t{0}".format(colored("Skipped", "yellow")))

    return movie


def main():
    """Main entry point for script"""
    from colorama import init
    import sys
    import argparse
    init()
    parser = argparse.ArgumentParser(
        description="Clean a MKV file name and all relevant files and tags")
    parser.add_argument("file",
                        metavar="file",
                        type=str,
                        help="MKV file to clean")
    args = parser.parse_args()
    movie = process_folder(args.file)
    if movie.error:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
