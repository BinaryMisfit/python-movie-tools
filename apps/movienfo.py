#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# NFO CREATOR
# ###

# Download and create a NFO file for a MP4 movie
#

# Current Version: 0.0.3
##########################################################################
import collections

MOVIE_DB_API = "dd51800087c3fe5c8feb21fd187776b2"


def build_nfo_xml(movie_data):
    """Build required NFO file XML"""
    from lxml import etree
    import dateutil.parser as parser
    result = collections.namedtuple(
        'nfo_data', 'xml imdb poster backdrop error')
    if movie_data.data is None:
        return result(None, None, None, None, 'Movie data is missing')

    if movie_data.sort_name is None:
        return result(None, None, None, None, 'Movie sort name is missing')

    if movie_data.rating is None:
        return result(None, None, None, None, 'Movie rating is missing')

    sort_name = movie_data.sort_name
    rating = movie_data.rating
    studio = movie_data.studio
    genre = movie_data.genre
    movie_data = movie_data.data
    movie_root = etree.Element('movie')
    movie_key = etree.SubElement(movie_root, 'title')
    movie_key.text = movie_data['title']
    movie_key = etree.SubElement(movie_root, 'originaltitle')
    movie_key.text = movie_data['original_title']
    movie_key = etree.SubElement(movie_root, 'sorttitle')
    movie_key.text = sort_name
    if 'belongs_to_collection' in movie_data and movie_data['belongs_to_collection'] is not None:
        movie_key = etree.SubElement(movie_root, 'set')
        movie_key.text = movie_data['belongs_to_collection']['name']

    movie_key = etree.SubElement(movie_root, 'rating')
    movie_key.text = str(movie_data['popularity'])
    movie_key = etree.SubElement(movie_root, 'year')
    movie_key.text = str(parser.parse(movie_data['release_date']).year)
    movie_key = etree.SubElement(movie_root, 'votes')
    movie_key.text = str(movie_data['vote_count'])
    movie_key = etree.SubElement(movie_root, 'plot')
    movie_key.text = movie_data['overview']
    movie_key = etree.SubElement(movie_root, 'tagline')
    movie_key.text = movie_data['tagline']
    movie_key = etree.SubElement(movie_root, 'runtime')
    movie_key.text = str(movie_data['runtime'])
    movie_key = etree.SubElement(movie_root, 'mpaa')
    movie_key.text = rating
    movie_key = etree.SubElement(movie_root, 'id')
    imdb_id = movie_data['imdb_id']
    movie_key.text = imdb_id
    movie_key = etree.SubElement(movie_root, 'genre')
    movie_key.text = genre
    movie_key = etree.SubElement(movie_root, 'studio')
    movie_key.text = studio
    directors = filter(lambda crew: crew['job'] == 'Director',
                       movie_data['credits']['crew'])
    director_count = len(directors)
    if directors is not None and director_count > 0:
        movie_key = etree.SubElement(movie_root, 'director')
        movie_key.text = directors[0]['name']

    cast = movie_data['credits']['cast']
    cast_count = len(cast)
    if cast is not None and cast_count > 0:
        for actor in cast:
            actor_key = etree.SubElement(movie_root, 'actor')
            actor_key_name = etree.SubElement(actor_key, 'name')
            actor_key_name.text = actor['name']
            actor_key_role = etree.SubElement(actor_key, 'role')
            actor_key_role.text = actor['character']

    poster = movie_data['poster_path']
    backdrop = movie_data['backdrop_path']
    movie_xml = etree.tostring(
        movie_root, encoding='UTF-8', xml_declaration=True, pretty_print=True)
    return result(movie_xml, imdb_id, poster, backdrop, None)


def generate_nfo(source_file, title, year):
    """Generate NFO content and data"""
    import disklibrary
    import movielibrary
    file_path = disklibrary.file_check(source_file, 'm4v')
    if file_path is None:
        print 'File %s not found or incorrect type' % source_file
        return 2

    file_parts = disklibrary.file_split(file_path)
    if file_parts is None:
        print 'Unable to parse file path'
        return 2

    movie_title = file_parts.file_title
    movie_year = movielibrary.movie_parse_year(file_parts.file_title)
    if title is not None:
        movie_title = title

    if year is not None:
        movie_year = year

    movie_title = movie_title.replace('(' + str(movie_year) + ')', '').strip()
    print 'Loading movie %s from %s' % (movie_title, movie_year)
    movie_data = movielibrary.movie_load_data(
        MOVIE_DB_API, movie_title, movie_year)
    if movie_data.error is not None:
        print movie_data.error
        return 2

    if movie_data.data is None:
        print 'Movie %s from %s not found' % (movie_title, movie_year)
        return 2

    movie_sort_name = movielibrary.movie_sort_name_builder(
        MOVIE_DB_API, movie_data.data)
    if movie_sort_name.error is not None:
        print movie_sort_name.error
        return 2

    print 'Loading additional data for %s' % movie_title
    movie_sort_name = movie_sort_name.sort_name
    movie_rating = movielibrary.movie_rating(
        movie_data.data['releases']['countries'])
    movie_genre = movielibrary.movie_imdb_genre(movie_data.data['imdb_id'])
    if movie_genre is None:
        movie_genre = movie_data.data['genres'][0]['name']

    movie_studio = movielibrary.movie_imdb_studio(movie_data.data['imdb_id'])
    if movie_studio is None:
        company_count = len(movie_data.data['production_companies'])
        if 'production_companies' in movie_data.data and company_count > 0:
            movie_studio = movie_data.data['production_companies'][0]['name']

    movie_info = collections.namedtuple(
        'movie_info', 'data genre studio sort_name rating')
    movie_data = movie_info(movie_data.data, movie_genre,
                            movie_studio, movie_sort_name, movie_rating)
    nfo_xml = build_nfo_xml(movie_data)
    if nfo_xml.error is not None:
        print nfo_xml.error
        return 2

    nfo_file = disklibrary.file_path(
        file_parts.file_path, file_parts.file_title + '.nfo')
    print 'Writing NFO file'
    disklibrary.file_delete(nfo_file)
    disklibrary.file_write(nfo_file, nfo_xml.xml)
    imdb_url = "http://www.imdb.com/title/" + nfo_xml.imdb + '/'
    disklibrary.file_write(nfo_file, imdb_url)
    if nfo_xml.poster is not None:
        poster_path = movielibrary.movie_poster(
            file_parts.file_path, nfo_xml.poster)
        save_poster = disklibrary.file_path(
            file_parts.file_path, file_parts.file_title + '-cover.jpg')
        print 'Downloading movie poster'
        if not disklibrary.file_rename(poster_path, save_poster):
            print 'Error creating movie cover'

    if nfo_xml.backdrop is not None:
        backdrop_path = movielibrary.movie_backdrop(
            file_parts.file_path, nfo_xml.backdrop)
        save_backdrop = disklibrary.file_path(
            file_parts.file_path, file_parts.file_title + '-fanart.jpg')
        print 'Downloading movie background'
        if not disklibrary.file_rename(backdrop_path, save_backdrop):
            print 'Error creating movie background'

    return 0


def main():
    """NFO Generator script"""
    import argparse
    import sys
    print 'Starting NFO creator'
    parser = argparse.ArgumentParser(
        description="Download and create a NFO file for a MP4 movie")
    parser.add_argument('file', metavar='file', type=str,
                        help='File to be used as source')
    parser.add_argument(
        '-t', '--title', help='The title of the movie', required=False)
    parser.add_argument('-y', '--year', type=int,
                        help='The year of release', required=False)
    args = parser.parse_args()
    output = generate_nfo(args.file, args.title, args.year)
    sys.exit(output)


if __name__ == "__main__":
    main()
