##########################################################################
# Movie Cleaner 
# ###

# Script to clean movie files and folders 

# Current Version: 0.0.1
##########################################################################


class MovieFolder(object):
    def __init__(self, mkv_file):
        self.mkv_file = mkv_file

    def __repr__(self):
        return '<MovieFolder mkv_file: %s' % self.mkv_file

    def __str__(self):
        return repr(self)


def main():
    """Main entry point for script"""
    import sys
    import argparse
    print 'Starting Movie Renamer'
    parser = argparse.ArgumentParser(
        description='Clean a MKV file name and all relevant files and tags')
    parser.add_argument('file', metavar='file', type=str,
                        help='MKV file to clean')
    args = parser.parse_args()
    print 'Checking file %s' % args.file
    output = 0
    sys.exit(output)


if __name__ == '__main__':
    main()
