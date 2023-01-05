# Copyright 2015 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# flake8: noqa F401

"""Database containing additional optional info about common gir files.

The gir files don't contain all the info we would like to have so this is a
collection of various information about the relation of the girs and their
projects and additional data fetched from other sources.

See tools/fetch-*.py for scripts which updates some of this info from external
sources.
"""

from .library import Library
from .project import PROJECTS, Project
from .summary import get_project_summary
from .util import (
    get_class_image_dir,
    get_class_image_path,
    get_doap_dir,
    get_doap_path,
    get_docref_dir,
    get_docref_path,
    load_doc_references,
)
