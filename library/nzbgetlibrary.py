#!/usr/bin/env python
"""Environment set to python"""

###################################################################################################
### NZBGET LIBRARY                                                                              ###

# Library of functions related to NZBGet and used to write plugins

# Current Version: 0.0.1
###################################################################################################

POST_PROCESS_SUCCESS = 93
POST_PROCESS_ERROR = 94
POST_PROCESS_NONE = 95


def check_options(required_options):
    """Checks the options required for NZBGet"""
    import os
    error = None
    for option in required_options:
        if option not in os.environ:
            error = option[6:]
            break

    return error
