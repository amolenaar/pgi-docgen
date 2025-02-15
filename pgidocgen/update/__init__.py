# Copyright 2018 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

from .clsimages import add_parser as add_parser_clsimages
from .doap import add_parser as add_parser_doap
from .docref import add_parser as add_parser_docref


def add_parser(subparser):
    add_parser_doap(subparser)
    add_parser_docref(subparser)
    add_parser_clsimages(subparser)
