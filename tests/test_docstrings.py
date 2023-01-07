# -*- coding: utf-8 -*-
# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

import pytest

from pgidocgen.namespace import get_base_types
from pgidocgen.repo import docstring_to_rest


class DummyRepo(object):

    missed_links = 0

    def __init__(self):
        self.types = {
            "g_rand_new_with_seed": ["GLib.Rand.new_with_seed"],
            "GQuark": ["GLib.Quark"],
            "GTypeInterface": ["GObject.TypeInterface"],
            "g_value_copy": ["GObject.Value.copy"],
            "GtkCellEditable": ["Gtk.CellEditable"],
            "gtk_tree_model_get": ["Gtk.TreeModel.get"],
            "GTK_TREE_VIEW_COLUMN_AUTOSIZE": ["Gtk.TreeViewColumnSizing.AUTOSIZE"],
            "AtkTextAttribute": ["Atk.TextAttribute"],
            "ATK_TEXT_ATTR_INVALID": ["Atk.TextAttribute.INVALID"],
            "GtkApplication": ["Gtk.Application"],
            "ATK_RELATION_NULL": ["Atk.RelationType.NULL"],
            "AtkObject": ["Atk.Object"],
            "AtkTable": ["Atk.Table"],
            "GtkSettings": ["Gtk.Settings"],
            "GtkContainer": ["Gtk.Container"],
            "GdkFrameTimings": ["Gdk.FrameTimings"],
            "GtkWidget": ["Gtk.Widget"],
            "GtkRecentFilterInfo": ["Gtk.RecentFilterInfo"],
        }
        self.types.update(get_base_types())

        self.docrefs = {
            "im-a-ref": "http://example.com",
        }

        self.type_structs = {
            "GtkWidgetClass": "Gtk.Widget",
        }

        self.instance_params = {"Gtk.TreeModel.get": "tree_model"}

    def lookup_gtkdoc_ref(self, doc_ref):
        return self.docrefs.get(doc_ref)

    def lookup_py_id(self, c_id):
        return self.types.get(c_id, [None])[0]

    def lookup_py_id_for_type_struct(self, c_id):
        return self.type_structs.get(c_id)

    def lookup_instance_param(self, py_id):
        return self.instance_params.get(py_id)


@pytest.fixture
def repo():
    return DummyRepo()


@pytest.fixture
def check(repo):
    def _check(text, expected, current_type=None, current_func=None):
        out = docstring_to_rest(repo, text, current_type, current_func)
        assert out == expected

    return _check


def test_invalid_xml(check):
    check("bla 1 < 3", "bla 1 < 3")
    check("bla 1 << 3", "bla 1 << 3")
    check("1<<$", "1<<$")
    check("1<<<G<", "1<<<G<")
    check("1>G", "1>G")
    check("negative value if a < b;", "negative value if a < b;")
    check("a & b", "a & b")
    check("&", "&")
    check("<", "<")
    check("<= 0 >=", "<= 0 >=")
    check("<a\nb>", "<a\nb>")
    check("<, == or >", "<, == or >")
    check("&,;", "&,;")


def test_prog(check):
    check(
        """
|[<!-- language="C" -->
&foo
b
]|""",
        """
.. code-block:: c

    &foo
    b\
""",
    )


def test_field(check):
    check(
        "#GtkRecentFilterInfo.contains",
        ":ref:`Gtk.RecentFilterInfo.contains <Gtk.RecentFilterInfo.fields>`",
    )


def test_booleans(check):
    check("%TRUE foo bar, %FALSE bar.", ":obj:`True` foo bar, :obj:`False` bar.")

    check("always returns %FALSE.", "always returns :obj:`False`.")

    # FIXME, should have a space after "="
    check("a expand=TRUE b", "a expand=:obj:`True` b")


def test_type(check):
    check(
        "a #GQuark id to identify the data",
        "a :obj:`GLib.Quark` id to identify the data",
    )

    check(
        "implementing a #GtkContainer: a",
        "implementing a :obj:`Gtk.Container`\\: a",
    )


def test_method(check):
    check("g_rand_new_with_seed()", ":obj:`GLib.Rand.new_with_seed`\\()")


def test_type_unmarked(check):
    check("The GTypeInterface structure", "The :obj:`GObject.TypeInterface` structure")

    check("GQuark", ":obj:`GLib.Quark`")


def test_params(check):
    check(
        "%TRUE if g_value_copy() with @src_type and @dest_type.",
        ":obj:`True` if :obj:`GObject.Value.copy`\\() with `src_type` and `dest_type`.",
    )

    check("@icon_set.", "`icon_set`.")

    check("if @page is complete.", "if `page` is complete.")

    check("in *@dest_x and ", "in `dest_x` and ")

    check("and a @foo\nbla", "and a `foo`\nbla")
    check("@one@two", "`one` `two`")

    check("at (@x, @y) bla", "at (`x`, `y`) bla")


def test_instance_params(check):
    check(
        "a @tree_model and a @foo",
        "a `self` and a `foo`",
        "Gtk.TreeModel",
        "Gtk.TreeModel.get",
    )


def test_inline_code(check):
    check(
        "To free this list, you can use |[ g_slist_free_full (list, (GDestroyNotify) g_object_unref); ]|",
        "To free this list, you can use ``g_slist_free_full (list, (GDestroyNotify) g_object_unref);``",
    )

    check("a |[ blaa()\n ]| adsad", "a ``blaa()`` adsad")


def test_escaped_xml(check):
    check(
        "target attribute on &lt;a&gt; elements.",
        "target attribute on <a> elements.",
    )

    check(
        "This is called for each unknown element under &lt;child&gt;.",
        "This is called for each unknown element under <child>.",
    )


def test_double(check):
    check("to double something", "to double something")


def test_docbook_linked_maybe_prop(check):
    check(
        '<link linkend="AtkObject--posy">posy</link>',
        ":obj:`posy <Atk.Object.props.posy>`",
    )


def test_docbook_linked(check):
    check(
        '<link linkend="gdouble"><type>double</type></link>',
        ":obj:`double <float>`",
    )

    check(
        '<link linkend="GtkWidget"><type>AtkTable</type></link>',
        ":obj:`Atk.Table <Gtk.Widget>`",
    )


def test_docbook_programlisting_single(check):
    check(
        """
<informalexample><programlisting>
gtk_entry_buffer_get_length (gtk_entry_get_buffer (entry));
</programlisting></informalexample>""",
        "``gtk_entry_buffer_get_length (gtk_entry_get_buffer (entry));``",
    )


def test_docbook_programlisting(check):
    check(
        """\
<programlisting>
foo;
bar;
</programlisting>\
""",
        """\

.. code-block:: none

    foo;
    bar;\
""",
    )


def test_docbook_programlisting_extra(check):
    check(
        """\
foo
<programlisting>
foo;
bar;
</programlisting>
bar\
""",
        """\
foo


.. code-block:: none

    foo;
    bar;

bar\
""",
    )


def test_docbook_literal(check):
    check(
        "the unique ID for @window, or <literal>0</literal> if the",
        "the unique ID for `window`, or ``0`` if the",
    )

    check(
        "you would\nwrite: <literal>;gtk_tree_model_get (model, iter, 0, &amp;place_string_here, -1)</literal>,\nwhere",
        "you would\nwrite\\: ``;gtk_tree_model_get (model, iter, 0, &place_string_here, -1)``,\nwhere",
    )

    check(
        "where <literal>place_string_here</literal> is a",
        "where ``place_string_here`` is a",
    )

    check(
        "a style class named <literal>level-</literal>@name",
        "a style class named ``level-`` `name`",
    )


def test_signal(check):
    check(
        "Emits the #GtkCellEditable::editing-done signal.",
        "Emits the :obj:`Gtk.CellEditable` :py:func:`::editing-done<Gtk.CellEditable.signals.editing_done>` signal.",
    )

    check("GtkWidget::foo_bar vfunc", "GtkWidget\\:\\:foo\\_bar vfunc")

    check("GtkWidgetClass::foo", "GtkWidgetClass\\:\\:foo")


def test_signal_no_type(check):
    check(
        "Returns the value of the ::columns signal.",
        "Returns the value of the :py:func:`::columns<Gtk.Widget.signals.columns>` signal.",
        "Gtk.Widget",
    )

    check(
        "this is some ::signal-foo blah",
        "this is some :py:func:`::signal-foo<Gtk.Widget.signals.signal_foo>` blah",
        "Gtk.Widget",
    )


def test_null(check):
    check("a filename or %NULL", "a filename or :obj:`None`")

    check("the NULL state or initial state", "the :obj:`None` state or initial state")

    check("%NULL-terminated", ":obj:`None`-terminated")


def test_docbook_type(check):
    check("is a <type>gchar*</type>\nto be filled", "is a ``gchar*``\nto be filled")


def test_constant(check):
    check(
        "Please note\nthat @GTK_TREE_VIEW_COLUMN_AUTOSIZE are inefficient",
        "Please note\nthat :obj:`Gtk.TreeViewColumnSizing.AUTOSIZE` are inefficient",
    )


def test_list(check):
    check(
        """\
bla bla
bla:

- The channel was just created, and has not been written to or read from yet.
  bla

- The channel is write-only.

foo
""",
        """bla bla
bla\\:


* The channel was just created, and has not been written to or read from yet.
  bla
* The channel is write-only.

foo
""",
    )


def test_docbook_itemizedlist(check):
    check(
        """\
<itemizedlist>
  <listitem>#GtkWidgetClass.get_request_mode()</listitem>
  <listitem>#GtkWidgetClass.get_preferred_width()</listitem>
  <listitem>#GtkWidgetClass.get_preferred_height()</listitem>
  <listitem>#GtkWidgetClass.get_preferred_height_for_width()</listitem>
  <listitem>#GtkWidgetClass.get_preferred_width_for_height()</listitem>
  <listitem>#GtkWidgetClass.get_preferred_height_and_baseline_for_width()</listitem>
</itemizedlist>
""",
        """
* :obj:`Gtk.Widget.do_get_request_mode`\\()
* :obj:`Gtk.Widget.do_get_preferred_width`\\()
* :obj:`Gtk.Widget.do_get_preferred_height`\\()
* :obj:`Gtk.Widget.do_get_preferred_height_for_width`\\()
* :obj:`Gtk.Widget.do_get_preferred_width_for_height`\\()
* :obj:`Gtk.Widget.do_get_preferred_height_and_baseline_for_width`\\()
""",
    )


def test_header(check):
    check(
        """\
GtkWidget is the base class all widgets in GTK+ derive from. It manages the
widget lifecycle, states and style.

# Height-for-width Geometry Management # {#geometry-management}

GTK+ uses a height-for-width (and width-for-height) geometry management
system. Height-for-width means that a widget can change how much
vertical space it needs, depending on the amount of horizontal space
that it is given (and similar for width-for-height). The most common
example is a label that reflows to fill up the available width, wraps
to fewer lines, and therefore needs less height.
""",
        """\
:obj:`Gtk.Widget` is the base class all widgets in GTK+ derive from. It manages the
widget lifecycle, states and style.


Height-for-width Geometry Management
    ..
        .

GTK+ uses a height-for-width (and width-for-height) geometry management
system. Height-for-width means that a widget can change how much
vertical space it needs, depending on the amount of horizontal space
that it is given (and similar for width-for-height). The most common
example is a label that reflows to fill up the available width, wraps
to fewer lines, and therefore needs less height.
""",
    )


def test_paragraphs(check):
    check(
        "foo,\nbar.\n\nfoo,\nbar.\n\nfoo,\nbar.\n",
        "foo,\nbar.\n\nfoo,\nbar.\n\nfoo,\nbar.\n",
    )


def test_unknown(check):
    check(
        " or #ATK_TEXT_ATTRIBUTE_INVALID if no match",
        "or #ATK\\_TEXT\\_ATTRIBUTE\\_INVALID if no match",
    )


def test_enum(check):
    check("or #ATK_RELATION_NULL if", "or :obj:`Atk.RelationType.NULL` if")


def test_escape_rest(check):
    check("table by initializing **selected", "table by initializing \\*\\*selected")

    check("Since: this is", "Since\\: this is")

    check(
        "unless it has handled or blocked `SIGPIPE'.",
        "unless it has handled or blocked \\`SIGPIPE'.",
    )


def test_type_plural(check):
    check("captions are #AtkObjects", "captions are :obj:`Atk.Objects <Atk.Object>`")

    check("foo #GdkFrameTiming", "foo :obj:`Gdk.FrameTiming <Gdk.FrameTimings>`")


def test_property(check):
    check(
        "the #GtkSettings:gtk-error-bell setting",
        "the :obj:`Gtk.Settings` :py:data:`:gtk-error-bell<Gtk.Settings.props.gtk_error_bell>` setting",
    )


def test_base_types(check):
    check("returns a gint*.", "returns a :obj:`int`.")

    check("a #gint** that", "a :obj:`int` that")

    check("returns a #gpointer", "returns a :obj:`object`")


def test_docbook_keycombo(check):
    check(
        "<keycombo><keycap>Control</keycap><keycap>L</keycap></keycombo>",
        "Control + L",
    )


def test_docbook_variablelist(check):
    check(
        '<variablelist role="params">\n\t  <varlistentry>\n\t    <term><parameter>chooser</parameter>&nbsp;:</term>\n\t    <listitem>\n\t      <simpara>\n\t\tthe object which received the signal.\n\t      </simpara>\n\t    </listitem>\n\t  </varlistentry>\n\t  <varlistentry>\n\t    <term><parameter>path</parameter>&nbsp;:</term>\n\t    <listitem>\n\t      <simpara>\n\t\tdefault contents for the text entry for the file name\n\t      </simpara>\n\t    </listitem>\n\t  </varlistentry>\n\t  <varlistentry>\n\t    <term><parameter>user_data</parameter>&nbsp;:</term>\n\t    <listitem>\n\t      <simpara>\n\t\tuser data set when the signal handler was connected.\n\t      </simpara>\n\t    </listitem>\n\t  </varlistentry>\n\t</variablelist>',
        """

chooser\\:
    the object which received the signal.


path\\:
    default contents for the text entry for the file name


user\\_data\\:
    user data set when the signal handler was connected.\
""",
    )


def test_varlistentry(check):
    check(
        "<varlistentry><term>#POPPLER_ANNOT_TEXT_ICON_NOTE</term></varlistentry>",
        "\n#POPPLER\\_ANNOT\\_TEXT\\_ICON\\_NOTE",
    )


def test_markdown_references(check):
    check("a [foo][bar] b [quux][baz]", "a 'foo [bar]' b 'quux [baz]'")

    check("a [foo][AtkObject]", "a :obj:`foo <Atk.Object>`")

    check("[gint][gint]", ":obj:`int`")

    check("a [foo][im-a-ref]", "a `foo <http://example.com>`__")

    check("a [foo][gtk-tree-model-get]", "a :obj:`foo <Gtk.TreeModel.get>`")

    check(
        "a [foo][GtkContainer--border-width]",
        "a :obj:`foo <Gtk.Container.props.border_width>`",
    )


def test_markdown_literal(check):
    check("`bla[0][1] = 3`", "``bla[0][1] = 3``")

    check("`<sadaf>`", "``<sadaf>``")


def test_vfuncs(check):
    check("#GtkWidget.get_request_mode()", ":obj:`Gtk.Widget.do_get_request_mode`\\()")


def test_various(check):

    check("foo <bar> bla <baz> g", "foo <bar> bla <baz> g")

    check(
        "appropriate.  #AtkTable summaries may themselves be (simplified) #AtkTables, etc.",
        "appropriate.  :obj:`Atk.Table` summaries may themselves be (simplified) :obj:`Atk.Tables <Atk.Table>`, etc.",
    )

    check("02:30 on March 14th 2010", "02\\:30 on March 14th 2010", "Gtk.Widget")


def test_markdown_code(check):
    check(
        """\
|[<!-- language="C" -->
    GdkEvent *event;
    GdkEventType type;

    type = event->type;
]|
""",
        """
.. code-block:: c

    GdkEvent *event;
    GdkEventType type;
    \n\
    type = event->type;
""",
    )

    check(
        """\
|[<!-- language="plain" -->
frame
├── border
├── <label widget>
╰── <child>
]|
""",
        """
.. code-block:: none

    frame
    ├── border
    ├── <label widget>
    ╰── <child>
""",
    )
