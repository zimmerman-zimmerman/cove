#!/usr/bin/env python
import os
import sys
import warnings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cove_ocds.settings")

    from django.core.management import execute_from_command_line

    sys.argv.insert(1, "cove_ocds")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        execute_from_command_line(sys.argv)
