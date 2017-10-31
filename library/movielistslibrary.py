#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE LISTS LIBRARY
# ###

# Library for generating various lists based on the movie database data.

# Current Version: 0.0.1
##########################################################################


def build_plist_data(meta_data, studio):
    """Build studio plist file"""
    from lxml import etree
    credit_data = meta_data['credits']
    plist = etree.Element('plist')
    plist.attrib['version'] = '1.0'
    plist_dictionary = etree.SubElement(plist, 'dict')
    if credit_data is not None:
        if 'cast' in credit_data:
            cast_data = credit_data['cast']
            cast_count = len(cast_data)
            if cast_count > 0:
                plist_cast_key = etree.SubElement(plist_dictionary, 'key')
                plist_cast_key.text = 'cast'
                plist_cast_array = etree.SubElement(plist_dictionary, 'array')
                for cast_member in cast_data:
                    plist_cast_array_dict = etree.SubElement(
                        plist_cast_array, 'dict')
                    plist_cast_member_key = etree.SubElement(
                        plist_cast_array_dict, 'key')
                    plist_cast_member_key.text = 'name'
                    plist_cast_member_name = etree.SubElement(
                        plist_cast_array_dict, 'string')
                    plist_cast_member_name.text = cast_member['name']

    if credit_data is not None:
        if 'crew' in credit_data:
            crew_data = credit_data['crew']
            crew_count = len(crew_data)
            if crew_count > 0:
                directors = filter(lambda crew:
                                   crew['job'] == 'Director', crew_data)
                director_count = len(directors)
                if director_count > 0:
                    plist_crew_key = etree.SubElement(plist_dictionary, 'key')
                    plist_crew_key.text = 'directors'
                    plist_crew_array = etree.SubElement(
                        plist_dictionary, 'array')
                    for director in directors:
                        plist_crew_array_dict = etree.SubElement(
                            plist_crew_array, 'dict')
                        plist_crew_member_key = etree.SubElement(
                            plist_crew_array_dict, 'key')
                        plist_crew_member_key.text = 'name'
                        plist_crew_member_name = etree.SubElement(
                            plist_crew_array_dict, 'string')
                        plist_crew_member_name.text = director['name']

                producers = filter(lambda crew:
                                   crew['job'] == 'Producer', crew_data)
                producer_count = len(producers)
                if producer_count > 0:
                    plist_crew_key = etree.SubElement(plist_dictionary, 'key')
                    plist_crew_key.text = 'producers'
                    plist_crew_array = etree.SubElement(
                        plist_dictionary, 'array')
                    for producer in producers:
                        plist_crew_array_dict = etree.SubElement(
                            plist_crew_array, 'dict')
                        plist_crew_member_key = etree.SubElement(
                            plist_crew_array_dict, 'key')
                        plist_crew_member_key.text = 'name'
                        plist_crew_member_name = etree.SubElement(
                            plist_crew_array_dict, 'string')
                        plist_crew_member_name.text = producer['name']

                writers = filter(lambda crew:
                                 crew['job'] == 'Screenplay', crew_data)
                writer_count = len(writers)
                if writer_count > 0:
                    plist_crew_key = etree.SubElement(plist_dictionary, 'key')
                    plist_crew_key.text = 'screenwriters'
                    plist_crew_array = etree.SubElement(
                        plist_dictionary, 'array')
                    for writer in writers:
                        plist_crew_array_dict = etree.SubElement(
                            plist_crew_array, 'dict')
                        plist_crew_member_key = etree.SubElement(
                            plist_crew_array_dict, 'key')
                        plist_crew_member_key.text = 'name'
                        plist_crew_member_name = etree.SubElement(
                            plist_crew_array_dict, 'string')
                        plist_crew_member_name.text = writer['name']

    if studio is not None:
        plist_studio_key = etree.SubElement(plist_dictionary, 'key')
        plist_studio_key.text = 'studio'
        plist_studio_member_name = etree.SubElement(plist_dictionary, 'string')
        plist_studio_member_name.text = studio

    credit_xml = etree.tostring(plist, encoding='UTF-8', xml_declaration=True, pretty_print=True,
                                doctype='<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" '
                                        '\"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">')
    return credit_xml


def build_nfo_xml(movie_data):
    """Create NFO XML"""
    from lxml import etree
    import dateutil.parser as parser
    import collections
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
