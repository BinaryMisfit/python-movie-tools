#!/usr/bin/env python
"""Environment set to python"""

##########################################################################
# MOVIE COUCHPOTATO NOTIFIER
# ###

# Notify CouchPotato of a new movie

# Current Version: 0.0.1
##########################################################################
COUCHPOTATO_UPLOAD_PATH = '/Services/CouchPotato2/Data/completed/'
COUCHPOTATO_NOTIFY_URL = 'http://localhost:6794/api/1e0598cb286b448b9515dc9a7427a775/' \
                         'renamer.scan/?media_folder=/Services/CouchPotato2/Data/completed/'


def generate_complete_url(source_file):
    """Generates and returns the notification URL"""
    notify_url = COUCHPOTATO_NOTIFY_URL + source_file
    return notify_url


def move_file(source_file):
    """Move file to correct location"""
    import shutil
    print 'Moving file to CouchPotato upload folder'
    target_folder = COUCHPOTATO_UPLOAD_PATH + source_file
    shutil.move(source_file, target_folder)


def check_file(source_file):
    """Check if file is already moved"""
    import os
    print 'Checking if file has to be moved to CouchPotato'
    if os.path.exists(source_file):
        return source_file

    target_folder = COUCHPOTATO_UPLOAD_PATH + source_file
    if os.path.exists(target_folder):
        return target_folder


def notify_couchpotato(source_file):
    """Notify CouchPotato of the new file"""
    import os
    import requests

    if os.path.exists(source_file):
        move_file(source_file)

    source_file = check_file(source_file)
    if source_file == "":
        return 0

    notify_url = generate_complete_url(source_file)
    print 'Notifying CouchPotato'
    try:
        requests.get(notify_url, timeout=1)
    except requests.exceptions.ReadTimeout:
        pass
    except:
        raise

    return 0


def main():
    """Main entry point for CouchPotato notifier"""
    import sys
    import argparse
    print 'Starting CouchPotato Notifier'
    parser = argparse.ArgumentParser(
        description='Renames a M4V file and all relevant files and tags')
    parser.add_argument('folder', metavar='folder', type=str,
                        help='Folder to prepare')
    args = parser.parse_args()
    print 'Preparing folder %s' % args.folder
    output = notify_couchpotato(args.folder)
    sys.exit(output)


if __name__ == '__main__':
    main()
