# Copyright 2013,2014 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

import os
import shutil

from .. import util
from ..util import get_csv_line
from . import genutil

_main_template = genutil.get_template(
    """\
{% if is_interface %}
==========
Interfaces
==========
{% else %}
=======
Classes
=======
{% endif %}

.. toctree::
    :maxdepth: 1

    {% for class in classes %}
    classes/{{ class.name }}
    {% endfor %}

"""
)


_py_template = genutil.get_template(
    """\
{% import '.genutil.UTIL' as util %}
{{ "=" * cls.fullname|length }}
{{ cls.fullname }}
{{ "=" * cls.fullname|length }}


Class Details
-------------

.. class:: {{ cls.fullname }}{{ cls.signature }}

    {{ util.render_info(cls.info)|indent(4, False) }}

    {% for pyprop in cls.pyprops %}
    .. py:attribute:: {{ pyprop.fullname }}

        {{ util.render_info(pyprop.info)|indent(8, False) }}

    {% endfor %}

    {% for method in cls.get_methods(static=True) %}
    .. classmethod:: {{ method.fullname }}{{ method.signature }}

        {{ method.signature_desc|indent(8, False) }}

        {{ util.render_info(method.info)|indent(8, False) }}

    {% endfor %}

    {% for method in cls.get_methods(static=False) %}
    .. method:: {{ method.fullname }}{{ method.signature }}

        {{ method.signature_desc|indent(8, False) }}

        {{ util.render_info(method.info)|indent(8, False) }}

    {% endfor %}

"""
)


_sub_template = genutil.get_template(
    """\
{% import '.genutil.UTIL' as util %}
{{ "=" * cls.fullname|length }}
{{ cls.fullname }}
{{ "=" * cls.fullname|length }}

{# ################################################ #}

.. inheritance-graph:: {{ cls.fullname }}

    {% for a in inheritance_nodes %}
    {% if a.is_interface %}
    {{ a.name }}: #3091D1
    {% elif a.is_abstract %}
    {{ a.name }}: #AAAAAA
    {% else %}
    {{ a.name }}: #75507B
    {% endif %}
    {% endfor %}

    {% for a, b in inheritance_edges %}
    {{ a.name }} -> {{ b.name }}
    {% endfor %}

{# ################################################ #}

{% if image_path %}
Example
-------

.. image:: {{ image_path }}

{% endif %}

{# ################################################ #}

{% if cls.is_interface %}
:Implementations: {% if not cls.subclasses %}None{% endif %}{% for name in cls.subclasses %}:class:`{{ name }}`{% if not loop.last %}, {% endif %}{% endfor %}
{% else %}
:Subclasses: {% if not cls.subclasses %}None{% endif %}{% for name in cls.subclasses %}:class:`{{ name }}`{% if not loop.last %}, {% endif %}{% endfor %}
{% endif %}

{# ################################################ #}

.. _{{ cls.fullname }}.methods:

Methods
-------

{% if cls.methods_inherited %}
:Inherited:
    {% for name, count in cls.methods_inherited %}
    :ref:`{{ name }} ({{ count }})<{{ name }}.methods>`{% if not loop.last %}, {% endif %}
    {% endfor %}

{% endif %}
{% if cls.gtype_struct_methods_inherited %}
:Structs:
    {% for name, count in cls.gtype_struct_methods_inherited %}
    :ref:`{{ name }} ({{ count }})<{{ name }}.methods>`{% if not loop.last %}, {% endif %}
    {% endfor %}


{% endif %}
{% if methods_summary_rows %}
.. csv-table::
    :widths: 1, 100

    {% for row in methods_summary_rows %}
        {{ row|indent(4, False) }}
    {% endfor %}

{% elif not cls.methods_inherited and not cls.gtype_struct_methods_inherited %}
None

{% endif %}

{# ################################################ #}

.. _{{ cls.fullname }}.vfuncs:

Virtual Methods
---------------

{% if cls.vfuncs_inherited %}
:Inherited:
    {% for name, count in cls.vfuncs_inherited %}
    :ref:`{{ name }} ({{ count }})<{{ name }}.vfuncs>`{% if not loop.last %}, {% endif %}
    {% endfor %}


{% endif %}
{% if vfuncs_summary_rows %}
.. csv-table::
    :widths: 1, 100

    {% for row in vfuncs_summary_rows %}
        {{ row|indent(4, False) }}
    {% endfor %}

{% elif not cls.vfuncs_inherited %}
None

{% endif %}

{# ################################################ #}

{% if cls.is_gobject %}

.. _{{ cls.fullname }}.props:

Properties
----------

{% if cls.properties_inherited %}
:Inherited:
    {% for name, count in cls.properties_inherited %}
    :ref:`{{ name }} ({{ count }})<{{ name }}.props>`{% if not loop.last %}, {% endif %}
    {% endfor %}


{% endif %}
{% if prop_lines %}
.. csv-table::
    :header: "Name", "Type", "Flags", "Short Description"
    :widths: 1, 1, 1, 100

    {% for line in prop_lines %}
    {{ line }}
    {% endfor %}
{% elif not cls.properties_inherited %}
None
{% endif %}

{% endif %}

{# ################################################ #}

{% if cls.child_properties or cls.child_properties_inherited %}

.. _{{ cls.fullname }}.child-props:

Child Properties
----------------

{% if cls.child_properties_inherited %}
:Inherited:
    {% for name, count in cls.child_properties_inherited %}
    :ref:`{{ name }} ({{ count }})<{{ name }}.child-props>`{% if not loop.last %}, {% endif %}
    {% endfor %}


{% endif %}

{% if cls.child_properties %}
.. csv-table::
    :header: "Name", "Type", "Default", "Flags", "Short Description"
    :widths: 1, 1, 1, 1, 100

    {% for line in child_prop_lines %}
    {{ line }}
    {% endfor %}
{% endif %}

{% endif %}

{# ################################################ #}

{% if cls.style_properties or cls.style_properties_inherited %}

.. _{{ cls.fullname }}.style-props:

Style Properties
----------------

{% if cls.style_properties_inherited %}
:Inherited:
    {% for name, count in cls.style_properties_inherited %}
    :ref:`{{ name }} ({{ count }})<{{ name }}.style-props>`{% if not loop.last %}, {% endif %}
    {% endfor %}


{% endif %}

{% if cls.style_properties %}
.. csv-table::
    :header: "Name", "Type", "Default", "Flags", "Short Description"
    :widths: 1, 1, 1, 1, 100

    {% for line in style_prop_lines %}
    {{ line }}
    {% endfor %}
{% endif %}

{% endif %}

{# ################################################ #}

{% if cls.is_gobject %}

.. _{{ cls.fullname }}.signals:

Signals
-------

{% if cls.signals_inherited %}
:Inherited:
    {% for name, count in cls.signals_inherited %}
    :ref:`{{ name }} ({{ count }})<{{ name }}.signals>`{% if not loop.last %}, {% endif %}
    {% endfor %}


{% endif %}
{% if sig_lines %}
.. csv-table::
    :header: "Name", "Short Description"
    :widths: 30, 70

    {% for line in sig_lines %}
    {{ line }}
    {% endfor %}
{% elif not cls.signals_inherited %}
None
{% endif %}

{% endif %}

{# ################################################ #}

.. _{{ cls.fullname }}.fields:

Fields
------

{% if cls.fields_inherited %}
:Inherited:
    {% for name, count in cls.signals_inherited %}
    :ref:`{{ name }} ({{ count }})<{{ name }}.fields>`{% if not loop.last %}, {% endif %}
    {% endfor %}


{% endif %}
{% if field_lines %}
.. csv-table::
    :header: "Name", "Type", "Access", "Description"
    :widths: 20, 1, 1, 100

    {% for row in field_lines %}
    {{ row|indent(4, False) }}
    {% endfor %}

{% elif not cls.fields_inherited %}
None

{% endif %}

{# ################################################ #}

Class Details
-------------

.. class:: {{ cls.fullname }}{{ cls.signature }}

    {% if cls.bases %}
    :Bases:
        {% for base in cls.bases %}
        :class:`{{ base.name }}`{% if not loop.last %}, {% endif %}
        {% endfor %}

    {% endif %}
    {% if not cls.is_interface %}
    :Abstract:
        {% if cls.is_abstract %}
        Yes
        {% else %}
        No
        {% endif%}
    {% endif %}
    {% if cls.gtype_struct %}
    :Structure:
        :class:`{{ cls.gtype_struct }}`

    {% endif %}

    {{ util.render_info(cls.info)|indent(4, False) }}

    {% for method in cls.get_methods(static=True) %}
    .. classmethod:: {{ method.fullname }}{{ method.signature }}

        {{ method.signature_desc|indent(8, False) }}

        {{ util.render_info(method.info)|indent(8, False) }}

    {% endfor %}

    {% for method in cls.get_methods(static=False) %}
    .. method:: {{ method.fullname }}{{ method.signature }}

        {{ method.signature_desc|indent(8, False) }}

        {{ util.render_info(method.info)|indent(8, False) }}

    {% endfor %}

    {% for method in cls.vfuncs %}
    .. method:: {{ method.fullname }}{{ method.signature }}
        :annotation:  virtual

        {{ method.signature_desc|indent(8, False) }}

        {{ util.render_info(method.info)|indent(8, False) }}

    {% endfor %}

{# ################################################ #}

{% if cls.signals %}
Signal Details
--------------

{% for signal in cls.signals %}
.. py:function:: {{ cls.fullname }}.signals.{{ signal.name }}{{ signal.signature }}

    :Signal Name: ``{{ signal.sig_name }}``
    :Flags: {{ signal.flags_string }}

    {{ signal.signature_desc|indent(4, False) }}

    {{ util.render_info(signal.info)|indent(4, False) }}

{% endfor %}
{% endif %}

{# ################################################ #}

{% if cls.properties %}
Property Details
----------------

{% for prop in cls.properties %}
.. py:data:: {{ cls.fullname }}.props.{{ prop.name }}

    :Name: ``{{ prop.prop_name }}``
    :Type: {{ prop.type_desc }}
    :Default Value: {{ prop.value_desc }}
    :Flags: {{ prop.flags_string }}

    {{ util.render_info(prop.info)|indent(4, False) }}

{% endfor %}
{% endif %}

"""
)


class ClassGenerator(genutil.Generator):
    """For GObjects an GInterfaces"""

    def __init__(self):
        self._classes = set()
        self._ifaces = set()
        self._pyclasses = set()

    def add_class(self, obj):
        if obj.is_interface:
            self._ifaces.add(obj)
        else:
            self._classes.add(obj)

    def add_pyclass(self, obj):
        self._pyclasses.add(obj)

    def get_names(self):
        names = []
        if self._ifaces:
            names.append("interfaces")
        if self._classes or self._pyclasses:
            names.append("classes")
        return names

    def is_empty(self):
        return not bool(self._classes) and not bool(self._ifaces) and not bool(self._pyclasses)

    def write(self, dir_):
        sub_dir = os.path.join(dir_, "classes")
        try:
            os.mkdir(sub_dir)
        except OSError:
            pass

        if self._ifaces:
            self._write(sub_dir, self._ifaces, True)

        if self._classes or self._pyclasses:
            classes = self._classes.copy()
            classes.update(self._pyclasses)
            self._write(sub_dir, classes, False)

    def _write(self, sub_dir, classes, is_interface):

        if is_interface:
            index_path = os.path.join(sub_dir, "..", "interfaces.rst")
        else:
            index_path = os.path.join(sub_dir, "..", "classes.rst")

        classes = sorted(classes, key=lambda x: x.name)

        # index rst
        with open(index_path, "wb") as h:
            text = _main_template.render(is_interface=is_interface, classes=classes)
            h.write(text.encode("utf-8"))

        for cls in classes:
            with open(os.path.join(sub_dir, cls.name) + ".rst", "wb") as h:
                if cls in self._pyclasses:
                    self._write_pyclass(h, cls)
                else:
                    self._write_class(h, cls)

    def _write_pyclass(self, h, cls):
        text = _py_template.render(
            cls=cls,
        )

        h.write(text.encode("utf-8"))

    def _write_class(self, h, cls):
        # methods
        methods = cls.get_methods(static=True)
        methods += cls.get_methods(static=False)

        summary_rows = []
        for func in methods:
            summary_rows.append(
                util.get_csv_line(
                    [
                        "*class*" if func.is_static else "",
                        ":py:func:`%s<%s>` %s" % (func.name, func.fullname, util.escape_rest(func.signature)),
                    ]
                )
            )
        methods_summary_rows = summary_rows

        # vfuncs
        summary_rows = []
        for func in cls.vfuncs:
            summary_rows.append(
                util.get_csv_line(
                    [
                        "",
                        ":py:func:`%s<%s>` %s" % (func.name, func.fullname, util.escape_rest(func.signature)),
                    ]
                )
            )
        vfuncs_summary_rows = summary_rows

        # props
        prop_lines = []
        for p in cls.properties:
            rst_target = cls.fullname + ".props." + p.name
            name = ":py:data:`%s<%s>`" % (p.prop_name, rst_target)
            short_desc = p.short_desc
            if p.info.deprecated:
                short_desc += " ``deprecated``"
            line = get_csv_line([name, p.type_desc, p.flags_short, short_desc])
            prop_lines.append(line)

        # child props
        child_prop_lines = []
        for p in cls.child_properties:
            name = "``%s``" % p.prop_name
            short_desc = p.short_desc
            if p.info.deprecated:
                short_desc += " ``deprecated``"
            line = get_csv_line([name, p.type_desc, p.value_desc, p.flags_short, short_desc])
            child_prop_lines.append(line)

        # style props
        style_prop_lines = []
        for p in cls.style_properties:
            name = "``%s``" % p.prop_name
            short_desc = p.short_desc
            if p.info.deprecated:
                short_desc += " ``deprecated``"
            line = get_csv_line([name, p.type_desc, p.value_desc, p.flags_short, short_desc])
            style_prop_lines.append(line)

        # signals
        sig_lines = []
        for sig in cls.signals:
            rst_target = cls.fullname + ".signals." + sig.name
            name_ref = ":py:func:`%s<%s>`" % (sig.sig_name, rst_target)
            short_desc = sig.short_desc
            if sig.info.deprecated:
                short_desc += " ``deprecated``"
            line = get_csv_line([name_ref, short_desc])
            sig_lines.append(line)

        # fields
        field_lines = []
        for field in cls.fields:
            field_lines.append(
                util.get_csv_line([field.name, field.type_desc, field.flags_string, field.info.desc])
            )

        def get_edges(tree):
            edges = []
            for cls, sub in tree:
                for base in sub:
                    edges.append((base[0], cls))
                edges.extend(get_edges(sub))
            return edges

        def get_nodes(tree):
            nodes = {}
            for cls, sub in tree:
                nodes[cls.name] = cls
                nodes.update(get_nodes(sub))
            return nodes

        # inheritance edges
        inheritance_edges = get_edges(cls.base_tree)
        inheritance_edges.sort(key=lambda x: x[0].name)

        inheritance_nodes = list(get_nodes(cls.base_tree).values())
        inheritance_nodes.sort(key=lambda x: x.name)

        # copy images
        if cls.image_path:
            target_dir = os.path.join(os.path.dirname(h.name), "images")
            try:
                os.mkdir(target_dir)
            except OSError:
                pass
            basename = os.path.basename(cls.image_path)
            shutil.copyfile(cls.image_path, os.path.join(target_dir, basename))
            image_path = "images/%s" % basename
        else:
            image_path = None

        # render
        text = _sub_template.render(
            cls=cls,
            methods_summary_rows=methods_summary_rows,
            vfuncs_summary_rows=vfuncs_summary_rows,
            prop_lines=prop_lines,
            child_prop_lines=child_prop_lines,
            style_prop_lines=style_prop_lines,
            sig_lines=sig_lines,
            field_lines=field_lines,
            inheritance_edges=inheritance_edges,
            inheritance_nodes=inheritance_nodes,
            image_path=image_path,
        )

        h.write(text.encode("utf-8"))
