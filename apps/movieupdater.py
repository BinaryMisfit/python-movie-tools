#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE UPDATER
# ###

# Downloads and sets meta data for M4V files based on file name
#
# Current Version: 0.0.1
##########################################################################
MOVIE_DB_API = "dd51800087c3fe5c8feb21fd187776b2"
"""Movie DB API Key"""


def update_file_tag(source_file, meta_data, sort_name, genre, rating, credit_xml, cover_file):
    """Update the tags for the file"""
    import os
    import struct
    from mutagen.mp4 import MP4, MP4Cover, MP4StreamInfoError
    try:
        update_file = MP4(source_file)
        if update_file.tags is not None:
            update_file.delete()

        directors = filter(lambda crew: crew['job'] == 'Director',
                           meta_data['credits']['crew'])
        director_count = len(directors)
        if director_count > 0:
            directors = directors[0]
        else:
            directors = None

        update_file['\xa9nam'] = meta_data['title']
        update_file['\xa9day'] = meta_data['release_date']
        update_file['\xa9gen'] = genre
        update_file['desc'] = meta_data['overview']
        update_file['ldec'] = meta_data['overview']
#        update_file['stik'] = str(unichr(9))
        update_file['hdvd'] = struct.pack('?', True)
        update_file['purd'] = meta_data['release_date']
        update_file['sonm'] = sort_name
        if credit_xml is not None:
            update_file['----:com.apple.iTunes:iTunMOVI'] = credit_xml

        if rating is not None:
            update_file['----:com.apple.iTunes:iTunEXTC'] = rating

        if directors is not None:
            if 'name' in directors:
                # noinspection PyTypeChecker
                update_file['soar'] = directors['name']
                # noinspection PyTypeChecker
                update_file['\xa9ART'] = directors['name']

        if cover_file is not None:
            with open(cover_file, "rb") as cover:
                update_file["covr"] = [
                    MP4Cover(cover.read(), imageformat=MP4Cover.FORMAT_JPEG)
                ]

            update_file.save()
            os.remove(cover_file)
    except MP4StreamInfoError as e:
        return '%s' % e.message

    return None


def movie_update(source_file):
    """Update movie with tag information"""
    import disklibrary
    import movielibrary
    import movielistslibrary
    file_path = disklibrary.file_check(source_file, 'm4v')
    if file_path is None:
        return 2

    file_parts = disklibrary.file_split(file_path)
    if file_parts is None:
        print 'Unable to parse file path'
        return 2

    movie_title = file_parts.file_title
    movie_year = movielibrary.movie_parse_year(file_parts.file_title)
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

    cover_link = None
    if 'poster_path' in movie_data.data and movie_data.data['poster_path'] is not None:
        poster_path = movielibrary.movie_poster(
            file_parts.file_path, movie_data.data['poster_path'])
        cover_link = disklibrary.file_path(
            file_parts.file_path, file_parts.file_title + '-cover.jpg')
        print 'Downloading movie cover'
        if not disklibrary.file_rename(poster_path, cover_link):
            print 'Error creating movie cover'

    print 'Retrieving additional information for %s' % movie_title
    sort_name = movielibrary.movie_sort_name_builder(
        MOVIE_DB_API, movie_data.data)
    genre = movielibrary.movie_imdb_genre(movie_data.data['imdb_id'])
    if genre is None:
        genre = movie_data.data['genres'][0]['name']

    studio = movielibrary.movie_imdb_studio(movie_data.data['imdb_id'])
    if studio is None:
        company_count = len(movie_data.data['production_companies'])
        if 'production_companies' in movie_data.data and company_count > 0:
            studio = movie_data.data['production_companies'][0]['name']

    if sort_name.error is not None:
        print sort_name.error

    rating = movielibrary.movie_rating(
        movie_data.data['releases']['countries'], True)
    print 'Generating cast and crew info for %s' % movie_title
    credit_xml = movielistslibrary.build_plist_data(movie_data.data, studio)
    print 'Updating movie tags for %s' % movie_title
    result = update_file_tag(file_parts.full_path, movie_data.data, sort_name.sort_name,
                             genre, rating, credit_xml, cover_link)
    if result is not None:
        print result
        return 1

    return 0


def main():
    """Main script interface for Movie Updater Script"""
    import argparse
    import sys
    print 'Starting Movie Updater'
    parser = argparse.ArgumentParser(
        description="Update the meta data for a M4V file")
    parser.add_argument('file', metavar='file', type=str,
                        help='File to be updated')
    args = parser.parse_args()
    print 'Checking file %s' % args.file
    output = movie_update(args.file)
    sys.exit(output)


if __name__ == "__main__":
    main()
