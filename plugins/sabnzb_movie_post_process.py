##########################################################################
# SABnzb Movie Post Process
# ###

# Provides post processing for movies downloaded via SABnzb

# Current Version: 0.0.1
##########################################################################
from collections import namedtuple


# def read_mkv_file(source_file):
#     """Retrieve MKV file information"""
#     import sys
#     import collections
#     import enzyme
#     from enzyme.exceptions import MalformedMKVError
#     result = collections.namedtuple('Result', 'mkv_file error')
#     with open(source_file, 'rb') as mkv_source:
#         try:
#             mkv_file = enzyme.MKV(mkv_source)
#         except MalformedMKVError:
#             return result(None, '[ERROR] %s' % sys.exc_info()[0])

#     return result(mkv_file, None)


def convert_mkv_file(folder):
    from lib_disk_util import check_contains_file
    result = namedtuple('Result', 'Error')
    list_files = check_contains_file(folder, '*.mkv')
    list_files_count = sum((1 for x in list_files))
    if list_files_count > 1:
        return result(False, 'Multiple files found')

    return result(False, None)


def check_valid_files(folder):
    from lib_disk_util import check_contains_file, file_size_format
    result = namedtuple('Result', 'Error')
    list_files = check_contains_file(folder, '*.mkv')
    if not list_files.error == None:
        return result(False, list_files.error)

    if list_files.result == None:
        return result(False, 'No files to process')

    files = list_files.result
    file_count = sum((1 for x in files))
    if (file_count > 1):
        check_file_size = 0
        for file in list_files:
            print(file.name + ' Size: ' + file_size_format(file.stat().st_size))
            if (file.stat().st_size > check_file_size):
                check_file_size = file.stat().st_size

    return result(True, None)


def main():
    """Main script interface for SABnzb Movie Post Process"""
    import sys
    import os
    sab_filename = os.environ['SAB_FILENAME']
    sab_category = os.environ['SAB_CAT']
    sab_directory = os.environ['SAB_COMPLETE_DIR']
    sab_pp_status = os.environ['SAB_PP_STATUS']
    if not sab_category == 'movies':
        print('Skipping - Not in movies category')
        sys.exit(0)
    if not sab_directory.strip():
        print('Skipping - Directory not supplied')
        sys.exit(0)
    if not int(sab_pp_status) == 0:
        print('Skipping - Post processing failed with status ' + sab_pp_status)
        sys.exit(0)

    print('##############################################')
    print('Processing:\t' + sab_filename)
    process_success = check_valid_files(sab_directory)
    if process_success.result:
        print('Validate Files:\t\tSuccess')
    else:
        print('Validate Files:\t\tFailed')

    if process_success.result:
        process_success = convert_mkv_file(sab_directory)
        if process_success.result:
            print('Convert MKV:\t\tSuccess')
        else:
            print('Convert MKV:\t\tFailed')
    else:
       print('Convert MKV:\t\tFailed')

    print('##############################################')
    if process_success.result:
        print('Completed:\t\t' + sab_filename)
        sys.exit(0)

    print('Failed ' + sab_filename + ':\t\t' + process_success.error)
    sys.exit(1)


if __name__ == '__main__':
    main()
