# -*- coding: utf-8 -*-
# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

import os

from . import genutil

_template = genutil.get_template(
    """\
{% import '.genutil.UTIL' as util %}
=========
Constants
=========

{% if constants %}
    {% for constant in constants %}
* :obj:`{{ constant.fullname }}`
    {% endfor %}

{% else %}
None

{% endif %}

Details
-------

{% if constants %}
    {% for constant in constants %}
.. data:: {{ constant.fullname }}
    :annotation: = {{ constant.value }}

    {{ util.render_info(constant.info)|indent(4, False) }}

    {% endfor %}
{% else %}
None

{% endif %}
"""
)


class ConstantsGenerator(genutil.Generator):
    def __init__(self):
        self._consts = set()

    def add_constant(self, const):
        self._consts.add(const)

    def get_names(self):
        return ["constants"]

    def is_empty(self):
        return not bool(self._consts)

    def write(self, dir_):
        path = os.path.join(dir_, "constants.rst")

        constants = sorted(self._consts, key=lambda c: c.name)

        with open(path, "wb") as h:
            text = _template.render(constants=constants)
            h.write(text.encode("utf-8"))
