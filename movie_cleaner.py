
##########################################################################
# Movie Cleaner 
# ###

# Script to clean movie files and folders 

# Current Version: 0.0.1
##########################################################################


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
