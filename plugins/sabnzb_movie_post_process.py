##########################################################################
# SABnzb Movie Post Process
# ###

# Provides post processing for movies downloaded via SABnzb

# Current Version: 0.0.1
##########################################################################


class SABResult(object):
    def __init__(self, result, data = None, error = None):
        self.result = result
        self.data = data
        self.error = error


def read_mkv_file(source_file):
    """Retrieve MKV file information"""
    import sys
    import enzyme
    from enzyme.exceptions import MalformedMKVError
    with open(source_file, 'rb') as mkv_source:
        try:
            mkv_file = enzyme.MKV(mkv_source)
            print(mkv_file)
        except MalformedMKVError:
            return SABResult(False, error = '[ERROR] %s' % sys.exc_info()[0])

    return SABResult(True)


def convert_mkv_file(files):
    file_count = sum((1 for x in files))
    if file_count == 0:
        return SABResult(False, error = 'Files not found')

    if file_count > 1:
        return SABResult(False, error = 'Multiple files found')

    for file in files:
        if file is None:
            return SABResult(False, error = 'File not found')
        result = read_mkv_file(str(file))
        if not result.error is None:
            return SABResult(False, error = result.error)

    return SABResult(False)


def check_valid_files(folder):
    from lib_disk_util import check_contains_file, file_size_format
    list_files = check_contains_file(folder, '*.mkv')
    if not list_files.result:
        return SABResult(False, error = list_files.error)

    if list_files.data is None:
        return SABResult(False, error = 'No files to process')

    files = list_files.data
    file_count = sum((1 for x in files))
    if (file_count > 1):
        check_file_size = 0
        for file in files:
            print(file.name + ' Size: ' + file_size_format(file.stat().st_size))
            if (file.stat().st_size > check_file_size):
                check_file_size = file.stat().st_size

    return SABResult(True)


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
    print('Processing:\t\t' + sab_filename)
    process_success = check_valid_files(sab_directory)
    if process_success.result:
        print('Validate Files:\t\tSuccess')
    else:
        print('Validate Files:\t\tFailed')

    if process_success.result:
        process_success = convert_mkv_file(process_success.data)
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

    if not process_success.error is None:
        print('failed ' + sab_filename + ':\t\t' + process_success.error)

    sys.exit(1)


if __name__ == '__main__':
    main()
