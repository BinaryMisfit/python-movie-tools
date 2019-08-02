##########################################################################
# SABnzb Movie Post Process
# ###

# Provides post processing for movies downloaded via SABnzb

# Current Version: 0.0.1
##########################################################################


def check_valid_files(folder):
    return False


def main():
    """Main script interface for SABnzb Movie Post Process"""
    import sys
    import os
    sab_final_name = os.environ['SAB_FINAL_NAME']
    sab_category = os.environ['SAB_CAT']
    sab_directory = os.environ['SAB_COMPLETE_DIR']
    sab_pp_status = os.environ['SAB_PP_STATUS']
    if not sab_category == 'movies':
        print('Skipping - Not in movies category')
        sys.exit(0)
    if not sab_directory.strip():
        print('Skipping - Directory not supplied')
        sys.exit(0)
    if not sab_pp_status == 0:
        print('Skipping - Post processing failed with status ' + sab_pp_status)
        sys.exit(0)

    process_success = False
    process_last_message = 'Script Loaded'
    print('##############################################')
    print('Processing: ' + sab_final_name)
    process_success = check_valid_files(sab_directory)
    if process_success:
        print('Validate Files:\tOK')
        process_last_message = 'Validate Files:\tOK'
        process_success
    else:
        print('Validate Files:\tFailed')
        process_last_message = 'Validate Files:\tFailed'
    print('##############################################')
    if process_success:
        process_last_message = 'Completed: ' + sab_final_name
        print(process_last_message)
        sys.exit(0)

    print('Failed ' + sab_final_name + ': ' + process_last_message)
    sys.exit(1)


if __name__ == '__main__':
    main()
