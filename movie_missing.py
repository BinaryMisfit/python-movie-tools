#!/usr/bin/env python

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
        movie_list = r.json()
        movie_path = [m['path'] for m in movie_list]
        movie_path = sorted(movie_path)
        return movie_path

    return None


def main():
    import sys
    from pathlib import Path
    movie_list = load_radarr_movies()
    if movie_list is None:
        sys.exit(1)

    movie_folder = Path('/Volumes/ProRaid/movies/')
    if movie_folder.exists:
        if movie_folder.is_dir:
            for movie in movie_folder.iterdir():
                if movie.is_dir:
                    if str(movie) not in movie_list:
                        print(str(movie))

    sys.exit(0)


if __name__ == '__main__':
    main()
