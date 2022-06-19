# -*- coding: utf-8 -*-
# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

import os

import gi
import pytest

gi.require_version("Gtk", "4.0")

from pgidocgen.util import (
    fake_bases,
    fake_subclasses,
    get_csv_line,
    get_signature_string,
    get_style_properties,
    instance_to_rest,
    is_attribute_owner,
    is_fundamental,
    is_method_owner,
    is_object,
    is_staticmethod,
    sanitize_instance_repr,
    unescape_parameter,
    unindent,
)


def test_get_signature_string():
    from gi.repository import Gio, GLib

    func = GLib.Error.__init__
    assert get_signature_string(func) == "()"
    assert get_signature_string(GLib.IOChannel.new_file) == "(filename, mode)"
    assert get_signature_string(GLib.IOChannel) == "(filedes=None, filename=None, mode=None, hwnd=None)"
    assert get_signature_string(GLib.MainLoop) == "(context=None)"
    assert get_signature_string(Gio.Menu.append) == "(label, detailed_action)"


def test_get_csv_line():
    assert get_csv_line(["foo"]) == '"foo"'
    assert get_csv_line(["foo", "bla\n"]) == '"foo","bla "'
    assert get_csv_line(["ä"]) == '"ä"'


def test_unindent():
    assert unindent("foo bar.", True) == "foo bar."
    assert unindent("foo bar.", False) == "foo bar."


def test_method_checks():
    from gi.repository import GLib

    assert not is_staticmethod(GLib.AsyncQueue, "push")
    assert is_staticmethod(GLib.Date, "new")
    assert is_staticmethod(GLib.IOChannel, "new_file")
    assert is_staticmethod(GLib.IOChannel, "new_file")
    assert is_staticmethod(GLib.Variant, "split_signature")


def test_is_method_owner():
    from gi.repository import GLib, Gtk

    assert not is_method_owner(GLib.IOError, "from_bytes")

    assert is_method_owner(Gtk.ActionGroup, "add_action")
    assert not is_method_owner(Gtk.Range, "get_has_tooltip")
    if os.name != "nt":
        assert is_method_owner(Gtk.Plug, "new")
    assert is_method_owner(Gtk.Viewport, "get_vadjustment")
    assert is_method_owner(Gtk.AccelGroup, "connect")
    assert not is_method_owner(Gtk.AboutDialog, "get_focus_on_map")


def test_is_attribute_owner():
    from gi.repository import GdkPixbuf

    getattr(GdkPixbuf.PixbufAnimation, "ref")
    assert not is_attribute_owner(GdkPixbuf.PixbufAnimation, "ref")


def test_class_checks():
    from gi.repository import GLib, GObject

    assert not is_fundamental(GLib.Error)
    assert is_fundamental(GObject.Object)
    assert is_fundamental(GObject.ParamSpec)
    assert not is_fundamental(object)


def test_is_object():
    from gi.repository import Gtk

    assert is_object(Gtk.Button)


def test_instance_to_rest():
    from gi.repository import Gtk

    def itr(gprop):
        return instance_to_rest(gprop.value_type.pytype, gprop.default_value)

    v = instance_to_rest(Gtk.AccelFlags, Gtk.AccelFlags.LOCKED)
    assert v == ":obj:`Gtk.AccelFlags.LOCKED` | :obj:`Gtk.AccelFlags.MASK`"

    v = instance_to_rest(int, 42)
    assert v == "``42``"

    v = instance_to_rest(Gtk.Button, None)
    assert v == ":obj:`None`"

    v = itr(Gtk.Widget.props.no_show_all)
    assert v == ":obj:`False`"

    v = instance_to_rest(Gtk.ImageType, Gtk.ImageType(int(Gtk.ImageType.EMPTY)))
    assert v == ":obj:`Gtk.ImageType.EMPTY`"

    v = itr(Gtk.AboutDialog.props.program_name)
    assert v == ":obj:`None`"

    v = itr(Gtk.IMContext.props.input_hints)
    assert v == ":obj:`Gtk.InputHints.NONE`"

    v = itr(Gtk.CellRendererAccel.props.accel_mods)
    assert v == "``0``"


def test_style_properties():
    from gi.repository import Gtk

    assert len(get_style_properties(Gtk.Paned)) == 1
    assert len(get_style_properties(Gtk.Widget)) == 17
    assert len(get_style_properties(Gtk.TreeView)) == 11


@pytest.mark.xfail
def test_fake_subclasses():
    from gi.repository import Gtk

    assert fake_subclasses(Gtk.Scrollable)[1] is Gtk.TreeView


def test_unescape():
    assert unescape_parameter("print_") == "print"
    assert unescape_parameter("exec_") == "exec"
    assert unescape_parameter("_print") == "-print"
    assert unescape_parameter("_3") == "3"


def test_fake_bases():
    from gi.repository import Atk, GObject

    assert fake_bases(Atk.ImplementorIface) == [GObject.GInterface]


def test_fake_bases_ignore_redundant():
    from gi.repository import Gtk

    assert fake_bases(Gtk.Dialog, ignore_redundant=True) == [Gtk.Window]


def test_sanitize_instance_repr():
    san = sanitize_instance_repr
    assert san("") == ""
    assert san("42") == "42"
    assert (
        san("<Color structure at 0x7f805e890b38 (ClutterColor at 0x2d028b0)>")
        == "<Color structure at 0x000000000000 (ClutterColor at 0x0000000)>"
    )

    assert san("<GType EvdConnection (31362256)>") == "<GType EvdConnection>"
