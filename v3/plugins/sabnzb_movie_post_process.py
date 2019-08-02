##########################################################################
# SABnzb Movie Post Process 
# ###

# Provides post processing for movies downloaded via SABnzb 

# Current Version: 0.0.1
##########################################################################


def main():
    """Main script interface for SABnzb Movie Post Process"""
    import sys
    try:
        (scriptname,directory,orgnzbname,jobname,reportnumber,category,group,postprocstatus,url) = sys.argv
    except:
        print("No commandline parameters found")
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
