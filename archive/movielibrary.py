#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE LIBRARY
# ###

# Library of movie related functions.

# Current Version: 0.0.2
##########################################################################


def movie_parse_year(movie_title):
    """Load movie year from title"""
    import re
    regex_year_match = r'\(\d{4}\)'
    if movie_title is None:
        return None

    result = re.search(regex_year_match, movie_title)
    if result is None:
        return None

    result = result.group()
    return result[1:-1]


def movie_load_data(api_key, movie_title, movie_year):
    """Load movie data from TMDB"""
    import collections
    import tmdbsimple as movie_db
    result = collections.namedtuple('movie_data', 'data error')
    if movie_title is None or movie_year is None:
        return result(None, 'Movie title or year missing')

    try:
        movie_db.API_KEY = api_key
        movie_result = movie_db.Search().movie(query=movie_title, year=movie_year)
    except movie_db.APIKeyError:
        return result(None, 'API key not supplied')

    if movie_result['total_results'] == 0:
        return result(None, 'Movie %s from %s not found' % (movie_title, movie_year))

    movie_result = movie_result['results'][0]
    movie_result = movie_db.Movies(movie_result['id']).info(
        append_to_response='credits,releases')
    return result(movie_result, None)


def movie_imdb_data(imdb_id):
    """Load movie data from IMDb"""
    from imdb import IMDb
    if imdb_id is None:
        return None

    imdb_db = IMDb()
    imdb_id = imdb_id[2:]
    movie_data = imdb_db.get_movie(imdb_id)
    return movie_data


def movie_collection_loader(api_key, collection_id):
    """Load the movie collection information"""
    import tmdbsimple as movie_db
    if collection_id is not None:
        try:
            movie_db.API_KEY = api_key
            return movie_db.Collections(collection_id).info()
        except movie_db.APIKeyError:
            return None


def movie_sort_name_builder(api_key, movie_data):
    """Generate the movie sort name"""
    import collections
    result = collections.namedtuple('movie_sort_name', 'sort_name error')
    if movie_data is None:
        return result(None, 'Movie data not supplied')

    collection_id = None
    if 'belongs_to_collection' in movie_data and movie_data['belongs_to_collection'] is not None:
        collection_id = movie_data['belongs_to_collection']['id']

    collection = None
    if collection_id is not None:
        collection = movie_collection_loader(
            api_key=api_key, collection_id=collection_id)

    movie_index = 1
    sort_name = None
    if collection is not None:
        movie_set_name = collection['name']
        part_count = len(collection['parts'])
        if 'parts' in collection and part_count > 0:
            movie_set = collection['parts']
            movie_set = sorted(movie_set, key=lambda k: k['release_date'])
            movie_index = next(index for (index, movie) in enumerate(movie_set)
                               if movie['title'] == movie_data['title'] and
                               movie['release_date'] == movie_data['release_date'])
            if movie_index is not None:
                movie_index += 1

            sort_name = movie_set_name + ' ' + str(movie_index)

    if sort_name is None:
        sort_name = movie_data['title'] + ' ' + str(movie_index)

    sort_name = reorder_name(sort_name)
    return result(sort_name, None)


def movie_rating(countries, itunes=False):
    """Load movie ratings"""
    mpaa_ratings = ['G', 'PG', 'PG-13', 'R', 'NC_17', 'Unrated']
    itunes_mpaa_ratings = [{'rating': 'NotRated', 'value': 'mpaa|NR|000|'},
                           {'rating': 'G', 'value': 'mpaa|G|100|'},
                           {'rating': 'PG', 'value': 'mpaa|PG|200|'},
                           {'rating': 'PG-13', 'value': 'mpaa|PG-13|300|'},
                           {'rating': 'R', 'value': 'mpaa|R|400|'},
                           {'rating': 'NC_17', 'value': 'mpaa|NC-17|500|'},
                           {'rating': 'Unrated', 'value': 'mpaa|Unrated|???|'}]
    if countries is None:
        if itunes:
            rating = filter(lambda mpaa:
                            mpaa['rating'] == 'Unrated', itunes_mpaa_ratings)
            rating_count = 0
            if rating is None:
                rating_count = len(rating)
            if rating_count > 0:
                rating = rating[0]
                if rating is not None:
                    if 'value' in rating:
                        return rating['value']

        return 'Unrated'

    rating = filter(lambda country:
                    country['certification'] in mpaa_ratings, countries)
    rating_count = 0
    if rating is not None:
        rating_count = len(rating)
    if rating_count > 0:
        for country_rating in rating:
            if isinstance(country_rating, list):
                rating = None

            if country_rating is not None:
                if 'certification' in country_rating:
                    rating = country_rating['certification']

            rating_count = 0
            if rating is not None:
                rating_count = len(rating)
            if rating is not None and rating_count > 0:
                break
    else:
        rating = None

    rating_count = 0
    if rating is not None:
        rating_count = len(rating)
    if rating is None or rating_count == 0:
        rating = 'Unrated'

    if itunes:
        rating = filter(lambda mpaa:
                        mpaa['rating'] == rating, itunes_mpaa_ratings)
        rating_count = len(rating)
        if rating_count > 0:
            rating = rating[0]
            if rating is not None:
                if 'value' in rating:
                    return rating['value']

    return rating


def movie_poster(local_path, poster_path):
    """Download movie poster locally"""
    import requests
    import shutil
    local_path += "/cover.jpg"
    poster_path = "http://image.tmdb.org/t/p/original" + poster_path
    poster = requests.get(poster_path, stream=True)
    if poster.status_code != 200:
        return 'Unable to download movie poster'

    with open(local_path, 'wb') as poster_file:
        poster.raw.decode_content = True
        shutil.copyfileobj(poster.raw, poster_file)

    return local_path


def movie_backdrop(local_path, backdrop_path):
    """Download movie backdrop locally"""
    import requests
    import shutil
    local_path += "/fanart.jpg"
    backdrop_path = "http://image.tmdb.org/t/p/original" + backdrop_path
    backdrop = requests.get(backdrop_path, stream=True)
    if backdrop.status_code != 200:
        return 'Unable to download movie backdrop'

    with open(local_path, 'wb') as backdrop_file:
        backdrop.raw.decode_content = True
        shutil.copyfileobj(backdrop.raw, backdrop_file)

    return local_path


def movie_imdb_rating(imdb_id, itunes=False):
    """Download IMDB ratings"""
    itunes_mpaa_ratings = [{'rating': 'NotRated', 'value': 'mpaa|NR|000|'},
                           {'rating': 'G', 'value': 'mpaa|G|100|'},
                           {'rating': 'PG', 'value': 'mpaa|PG|200|'},
                           {'rating': 'PG-13', 'value': 'mpaa|PG-13|300|'},
                           {'rating': 'R', 'value': 'mpaa|R|400|'},
                           {'rating': 'NC_17', 'value': 'mpaa|NC-17|500|'},
                           {'rating': 'NC-17', 'value': 'mpaa|NC-17|500|'},
                           {'rating': 'Unrated', 'value': 'mpaa|Unrated|???|'}]
    from imdb import IMDb
    if imdb_id is None:
        return None

    rating = None
    imdb_db = IMDb()
    imdb_id = imdb_id[2:]
    movie_data = imdb_db.get_movie(imdb_id)
    if movie_data.has_key('certificates'):
        for certificate in movie_data['certificates']:
            certificate_data = certificate.split(':')
            if certificate_data[0] in ['USA', 'UK']:
                if certificate_data[1] == 'Not Rated':
                    continue

                if certificate_data[1] in ['15']:
                    rating = 'PG-13'
                    break

    rating_count = len(rating)
    if rating is None or rating_count == 0:
        rating = 'Unrated'

    if itunes:
        rating = filter(lambda mpaa:
                        mpaa['rating'] == rating, itunes_mpaa_ratings)
        rating_count = len(rating)
        if rating_count > 0:
            rating = rating[0]
            if rating is not None:
                if 'value' in rating:
                    return rating['value']

    return rating


def movie_imdb_genre(imdb_id):
    """Download IMDB movie genre"""
    from imdb import IMDb
    if imdb_id is None:
        return None

    imdb_db = IMDb()
    imdb_id = imdb_id[2:]
    movie_data = imdb_db.get_movie(imdb_id)
    if movie_data.has_key('genre'):
        return movie_data['genre'][0]

    return None


def movie_imdb_studio(imdb_id):
    """Download IMDB movie studio"""
    from imdb import IMDb
    if imdb_id is None:
        return None

    imdb_db = IMDb()
    imdb_id = imdb_id[2:]
    movie_data = imdb_db.get_movie(imdb_id)
    if movie_data.has_key('production companies'):
        for company in movie_data['production companies']:
            imdb_db.update(company)
            if company.has_key('distributors'):
                continue

            if company.has_key('miscellaneous companies'):
                continue

            if company.has_key('special effects companies'):
                continue

            if 'country' not in company.keys():
                continue

            if company['country'] not in ['[us]', '[gb]']:
                continue

            return company['name']

    return None


def reorder_name(check_name):
    """Move The to the back of file name"""
    if check_name is None:
        return None

    if check_name.startswith('The '):
        check_name = check_name.replace('The ', '').strip()
        check_name += ', The'

    return check_name
