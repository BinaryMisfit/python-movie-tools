#!/usr/bin/env python3

##########################################################################
# Movie Missing Finder
# ###

# Script to find all movies not on Radarr

# Current Version: 0.0.1
##########################################################################
radarr_api_url = "https://radarr.senselesslyfoolish.com/api"
radarr_api_key = '3070b92e6c3f47d88dd3d6682089f2ae'


def load_radarr_movies():
    from requests import get
    get_movies_url = ("{0}/movie?apiKey={1}").format(radarr_api_url,
                                                     radarr_api_key)
    r = get(get_movies_url)
    if (r.status_code == 200):
        movie_path = r.json()
        return movie_path

    return None


def find_movie(movie_list, path):
    for movie in movie_list:
        if movie['folderName'] == path:
            return movie
    return None


def check_movie(movie_list, movie):
    print(str(movie))
    mkv_files = movie.glob('*.mkv')
    has_movie = mkv_files is not None
    movie_info = find_movie(movie_list, str(movie))
    if movie_info is not None:
        if not movie_info["downloaded"]:
            print(('Movie Found: {0}').format(has_movie))
    else:
        print(('Movie Found: {0}. Not in Radarr').format(has_movie))

    if has_movie:
        return 1
    return 0


def main():
    import sys
    from pathlib import Path
    movie_list = load_radarr_movies()
    if movie_list is None:
        sys.exit(1)

    movie_folder = Path('/Volumes/ProRaid/movies/')
    movie_count = 0
    if movie_folder.exists():
        if movie_folder.is_dir():
            for movie in movie_folder.iterdir():
                if movie.is_dir():
                    movie_count += int(check_movie(movie_list, movie))

    print(("Total movies found: {0}").format(movie_count))
    sys.exit(0)


if __name__ == '__main__':
    main()
