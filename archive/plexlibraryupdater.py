#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# Project: .scripts
# Filename: PlexLibraryUpdater
# User: Willie Roberts
# Date: 2016-09-12
##########################################################################
MOVIE_DB_API = "dd51800087c3fe5c8feb21fd187776b2"


def update_rating(tmdb, imdb):
    """Calculate new rating"""
    if tmdb is None or imdb is None:
        return 0

    tmdb_rating = 0
    if 'vote_average' in tmdb:
        tmdb_rating = tmdb['vote_average']

    imdb_rating = 0
    if imdb.has_key('rating'):
        imdb_rating = imdb['rating']

    rating_list = [tmdb_rating, imdb_rating]
    return round(sum(rating_list) / len(rating_list), 1)


def update_content_rating(tmdb):
    """Update content rating"""
    import movielibrary
    if tmdb is None:
        return 'NotRated'

    tmdb_content_rating = movielibrary.movie_rating(
        tmdb['releases']['countries'])
    content_rating = tmdb_content_rating
    if tmdb_content_rating is None or tmdb_content_rating == 'Unrated':
        content_rating = movielibrary.movie_imdb_rating(tmdb['imdb_id'])

    if 'adult' in tmdb:
        if tmdb['adult']:
            content_rating = 'NC-17'

    return content_rating


def update_rating_count(tmdb, imdb):
    """Updating rating count"""
    if tmdb is None or imdb is None:
        return 0

    tmdb_count = 0
    if 'vote_count' in tmdb:
        tmdb_count = tmdb['vote_count']

    imdb_count = 0
    if imdb.has_key('votes'):
        imdb_count = imdb['votes']

    count_list = [tmdb_count, imdb_count]
    return sum(count_list) / len(count_list)


def update_genres(tmdb, imdb):
    """Update Genres"""
    genre_map = {'Sci-Fi': 'Science Fiction'}
    if tmdb is None or imdb is None:
        return None

    genres = []
    if 'genres' in tmdb:
        for genre in tmdb['genres']:
            genres.append(genre['name'])

    if imdb.has_key('genres'):
        for genre in imdb['genres']:
            if genre in genre_map.keys():
                genre = genre_map[genre]

            if genre not in genres:
                genres.append(genre)

    return sorted(genres)


def update_tagline(tmdb, imdb):
    """Update Tag Line"""
    if tmdb is None or imdb is None:
        return None

    tagline = None
    if 'tagline' in tmdb:
        tagline = tmdb['tagline']

    return tagline


def update_collection(api_key, tmdb):
    """Update collection"""
    import movielibrary
    if tmdb is None:
        return None

    collection_id = None
    if 'belongs_to_collection' in tmdb:
        collection = tmdb['belongs_to_collection']
        if collection is not None:
            collection_id = collection['id']

    if collection_id is not None:
        collection = movielibrary.movie_collection_loader(
            api_key=api_key, collection_id=collection_id)
        if 'name' in collection:
            return collection['name']

    return None


def update_content_rating_age(content_rating):
    """Update content rating age"""
    rating_age_map = [{'rating': 'G', 'age': 0},
                      {'rating': 'PG', 'age': 13},
                      {'rating': 'PG-13', 'age': 13},
                      {'rating': 'R', 'age': 18},
                      {'rating': 'NC-17', 'age': 18}]
    rating_age_found = filter(lambda rating_age: rating_age[
                              'rating'] == content_rating, rating_age_map)
    if len(rating_age_found) > 0:
        rating_age_found = rating_age_found[0]
        if rating_age_found is None:
            return 0

        return rating_age_found['age']

    return 0


def main():
    """Main entry point for Plex Library Update"""
    import os
    import sys
    import argparse
    import plexlibrary
    import movielibrary
    print 'Starting Plex Library Updater'
    parser = argparse.ArgumentParser(
        description="Update Plex library meta data")
    parser.add_argument('folder', metavar='folder',
                        type=str, help='Folder to be checked')
    args = parser.parse_args()
    source_folder = args.folder
    if source_folder is None or not os.path.isdir(source_folder):
        print 'Folder %s not found or valid' % source_folder
        sys.exit(2)

    content_list = os.listdir(source_folder)
    if content_list is None or len(content_list) == 0:
        print 'No files or folders found'
        sys.exit(2)

    os.nice(10)
    print 'Processing folder %s' % source_folder
    for item in content_list:
        item_folder = os.path.join(source_folder, item)
        if not os.path.isdir(item_folder):
            continue

        library_content = os.listdir(item_folder)
        if library_content is None or len(library_content) == 0:
            continue

        item_max_count = 3
        item_count = 0
        for library_item in sorted(library_content):
            if library_item.endswith('.bundle'):
                library_folder = os.path.join(item_folder, library_item)
                library_item_xml = library_folder + \
                    '/Contents/com.plexapp.agents.localmedia/Info.xml'
                if not os.path.isfile(library_item_xml):
                    continue

                original_items = {}
                unchecked_items = {}
                update_items = {}
                processed_keys = []
                # Load data from TMDB and IMDB
                movie_title = plexlibrary.movie_title(
                    library_xml=library_item_xml)
                processed_keys.append('title')
                movie_year = plexlibrary.movie_year(
                    library_xml=library_item_xml)
                processed_keys.append('year')
                print '{0:40}'.format('%s:%s' %
                                      (item, library_item.replace('.bundle', ''))),
                print '{0:40}'.format('%s (%s)' %
                                      (movie_title[:32], movie_year)),
                tmdb_data = movielibrary.movie_load_data(api_key=movie_db_api, movie_title=movie_title,
                                                         movie_year=movie_year)
                tmdb_data = tmdb_data.data
                print '{0:20}'.format('TMDB: Loaded'),
                imdb_data = movielibrary.movie_imdb_data(tmdb_data['imdb_id'])
                print '{0:20}'.format('IMDB: Loaded'),

                # Retrieve movie rating
                movie_rating = plexlibrary.check_key(
                    library_xml=library_item_xml, key='rating')
                processed_keys.append('rating')
                original_items['rating'] = movie_rating
                if movie_rating is None or len(movie_rating) == 0:
                    movie_rating = 0

                updated_rating = update_rating(tmdb=tmdb_data, imdb=imdb_data)
                if float(movie_rating) != float(updated_rating):
                    update_items['rating'] = updated_rating

                # Retrieve sort tile
                movie_sort_tile = plexlibrary.check_key(
                    library_xml=library_item_xml, key='title_sort')
                processed_keys.append('title_sort')
                unchecked_items['title_sort'] = movie_sort_tile

                # Retrieve art
                movie_art = plexlibrary.check_key(
                    library_xml=library_item_xml, key='art')
                processed_keys.append('art')
                unchecked_items['art'] = movie_art

                # Retrieve chapters
                movie_chapters = plexlibrary.check_key(
                    library_xml=library_item_xml, key='chapters')
                processed_keys.append('chapters')
                unchecked_items['chapters'] = movie_chapters

                # Retrieve movie content rating
                movie_content_rating = plexlibrary.check_key(
                    library_xml=library_item_xml, key='content_rating')
                original_items['content_rating'] = movie_content_rating
                updated_content_rating = update_content_rating(tmdb=tmdb_data)
                if movie_content_rating != updated_content_rating:
                    update_items['content_rating'] = updated_content_rating

                # Retrieve writer list
                movie_writers = plexlibrary.check_key(
                    library_xml=library_item_xml, key='writers')
                processed_keys.append('writers')
                unchecked_items['writers'] = movie_writers

                # Retrieve themes
                movie_themes = plexlibrary.check_key(
                    library_xml=library_item_xml, key='themes')
                processed_keys.append('themes')
                unchecked_items['themes'] = movie_themes

                # Retrieve quotes
                movie_quotes = plexlibrary.check_key(
                    library_xml=library_item_xml, key='quotes')
                processed_keys.append('quotes')
                unchecked_items['quotes'] = movie_quotes

                # Retrieve duration
                movie_duration = plexlibrary.check_key(
                    library_xml=library_item_xml, key='duration')
                processed_keys.append('duration')
                unchecked_items['duration'] = movie_duration

                # Retrieve genres
                movie_genres = plexlibrary.check_key(
                    library_xml=library_item_xml, key='genres')
                processed_keys.append('genres')
                original_items['genres'] = movie_genres
                updated_genres = update_genres(tmdb=tmdb_data, imdb=imdb_data)
                if movie_genres is None:
                    movie_genres = []

                if len(movie_genres) != len(updated_genres) and len(updated_genres) > 0:
                    update_items['genres'] = updated_genres

                # Retrieve tag line
                movie_tagline = plexlibrary.check_key(
                    library_xml=library_item_xml, key='tagline')
                processed_keys.append('tagline')
                original_items['tagline'] = movie_tagline
                updated_tagline = update_tagline(
                    tmdb=tmdb_data, imdb=imdb_data)
                if movie_tagline != updated_tagline:
                    update_items['tagline'] = updated_tagline

                # Retrieve content rating age
                movie_content_rating_age = plexlibrary.check_key(
                    library_xml=library_item_xml, key='content_rating_age')
                processed_keys.append('content_rating_age')
                original_items['content_rating_age'] = movie_content_rating_age
                if movie_content_rating_age is None:
                    movie_content_rating_age = -1

                updated_content_rating_age = update_content_rating_age(
                    updated_content_rating)
                if int(updated_content_rating_age) != int(movie_content_rating_age):
                    update_items[
                        'content_rating_age'] = updated_content_rating_age

                # Retrieve rating count
                movie_rating_count = plexlibrary.check_key(
                    library_xml=library_item_xml, key='rating_count')
                processed_keys.append('rating_count')
                original_items['content_rating_count'] = movie_rating_count
                if movie_rating_count is None:
                    movie_rating_count = -1

                updated_rating_count = update_rating_count(
                    tmdb=tmdb_data, imdb=imdb_data)
                if int(updated_rating_count) != int(movie_rating_count):
                    update_items['rating_count'] = updated_rating_count

                # Retrieve collection
                movie_collection = plexlibrary.check_key(
                    library_xml=library_item_xml, key='collections')
                processed_keys.append('collections')
                if movie_collection is not None and len(movie_collection) > 0:
                    movie_collection = movie_collection[0]

                if movie_collection is not None:
                    original_items['collections'] = movie_collection
                    updated_collection = update_collection(
                        api_key=movie_db_api, tmdb=tmdb_data)
                    if updated_collection != movie_collection and updated_collection is not None:
                        update_items['collections'] = [updated_collection]

                # Build original value list
                original_list = 'Original: '
                for item_key in sorted(original_items):
                    original_list += '[%s: %s] ' % (item_key,
                                                    original_items[item_key])

                # Build unchecked value list
                unchecked_list = 'Unchecked: '
                for item_key in sorted(unchecked_items):
                    unchecked_list += '[%s: %s] ' % (item_key,
                                                     unchecked_items[item_key])

                # Build updated value list
                update_list = 'Updates: '
                for item_key in sorted(update_items):
                    update_list += '[%s: %s] ' % (item_key,
                                                  update_items[item_key])

                # Update Plex Library
                # item_count += 1
                if len(update_items) > 0:
                    updated_xml = plexlibrary.update_library_xml(
                        library_item_xml, update_items)
                    # temp_xml = os.path.join('/Users/wirob/Downloads', '%s.xml' % movie_title)
                    # plexlibrary.write_xml(updated_xml, temp_xml)
                    plexlibrary.write_xml(updated_xml, library_item_xml)
                    item_count += 1
                    print 'Updated: Yes'
                    print original_list.strip()
                    print unchecked_list.strip()
                    print update_list.strip()
                else:
                    print 'Updated: No'
                    print original_list.strip()
                    print unchecked_list.strip()

                plexlibrary.iterate_library_xml(
                    library_xml=library_item_xml, exclude_items=processed_keys)
                tmdb_keys_processed = [
                    'vote_average', 'genres', 'releases', 'vote_count', 'adult']
                tmdb_keys = []
                for key in tmdb_data.keys():
                    if key not in tmdb_keys_processed:
                        tmdb_keys.append(key)

                imdb_keys_processed = [
                    'mpaa', 'certificates', 'genres', 'imdb_id', 'votes']
                imdb_keys = []
                for key in imdb_data.keys():
                    if key not in imdb_keys_processed:
                        imdb_keys.append(key)

                print sorted(tmdb_keys)
                print sorted(imdb_keys)
                if item_count >= item_max_count:
                    break

        if item_count == item_max_count:
            break

    print 'Processed folder %s' % source_folder
    sys.exit(0)


if __name__ == '__main__':
    main()
