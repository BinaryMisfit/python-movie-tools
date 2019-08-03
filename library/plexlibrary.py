#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# Project: .scripts
# Filename: PlexLibrary
# User: Willie Roberts
# Date: 2016-09-13
##########################################################################


def iterate_library_xml(library_xml, exclude_items=None):
    """Read Plex library XML"""
    from lxml import etree
    if library_xml is None:
        return

    xml = etree.parse(library_xml)
    xml = xml.getroot()
    if exclude_items is None:
        exclude_items = []

    for element in xml:
        if element.tag not in exclude_items:
            print '%s' % element.tag,

    print ''


def update_library_xml(library_xml, updated_values):
    """Update Plex library XML"""
    from lxml import etree
    if library_xml is None:
        return

    xml = etree.parse(library_xml)
    xml = xml.getroot()
    for element in xml:
        if element.tag in updated_values:
            update_value = updated_values[element.tag]
            if isinstance(update_value, basestring):
                element.text = unicode(update_value)
                continue

            if isinstance(update_value, int):
                element.text = unicode(update_value)
                continue

            if isinstance(update_value, list):
                new_element = etree.Element(element.tag)
                for item in update_value:
                    if isinstance(item, dict):
                        print 'Dictionary'

                    if isinstance(item, basestring):
                        new_element_child = etree.SubElement(
                            new_element, 'item')
                        new_element_child.attrib['index'] = unicode(
                            update_value.index(item))
                        new_element_child.text = unicode(item)

                xml.replace(element, new_element)
                continue

    xml = etree.tostring(xml, pretty_print=True)
    return xml


def write_xml(xml, file_name):
    """Write XML file"""
    from lxml import etree
    if xml is None:
        return

    if file_name is None:
        return

    xml = etree.fromstring(xml)
    xml = etree.ElementTree(xml)
    xml.write(file_name, pretty_print=True,
              encoding='utf-8', xml_declaration=True)


def check_key(library_xml, key):
    """Check XML key"""
    from lxml import etree
    if library_xml is None:
        return

    xml = etree.parse(library_xml)
    node = xml.xpath('//Movie/%s' % key)
    for element in node:
        element_count = len(element)
        if element_count > 0:
            value = []
            for child in element:
                if child.tag == 'item' and 'index' in child.keys():
                    value_item = child.text.strip()
                    value_count = len(value_item)
                    if value_count > 0:
                        value.append(value_item)

                if child.tag == 'item' and 'media' in child.keys():
                    value_item = {'external': child.get('external'), 'url': child.get(
                        'url'), 'media': child.get('media'), 'sort_order': child.get('sort_order')}
                    value.append(value_item)

            value_count = len(value)
            if value_count == 0:
                return None

            return value

        element_count = len(element)
        if element_count == 0:
            if element.text is None:
                return None

            value = element.text.strip()
            value_count = len(value)
            if value_count == 0:
                return None

            return value


def movie_title(library_xml):
    """Read movie title"""
    from lxml import etree
    if library_xml is None:
        return

    xml = etree.parse(library_xml)
    return xml.xpath('//Movie/title')[0].text


def movie_year(library_xml):
    """Read movie year"""
    from lxml import etree
    if library_xml is None:
        return

    xml = etree.parse(library_xml)
    return xml.xpath('//Movie/year')[0].text
