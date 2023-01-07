# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.


import pytest

from pgidocgen.docobj import Class, Constant, Flags, Function, PyClass, get_hierarchy
from pgidocgen.overrides import parse_override_docs
from pgidocgen.repo import Repository


def find(l, name):
    for i in l:
        if i.name == name:
            return i
    raise LookupError


@pytest.mark.xfail(reason="Currently no overrides")
def test_parse_override_docs():
    docs = parse_override_docs("Gtk", "3.0")
    assert "Gtk.Widget.translate_coordinates" in docs
    assert docs["Gtk.Widget.translate_coordinates"]


def test_override_method():
    repo = Repository("Gtk", "3.0")
    Gtk = repo.import_module()
    func = Function.from_object(
        "Gtk.Widget",
        "translate_coordinates",
        Gtk.Widget.translate_coordinates,
        repo,
        Gtk.Widget,
    )
    assert func.signature == "(dest_widget, src_x, src_y)"


def test_method_inheritance():
    repo = Repository("Atk", "1.0")
    Atk = repo.import_module()
    klass = Class.from_object(repo, Atk.Plug)
    assert [x[0] for x in klass.methods_inherited] == ["Atk.Object", "GObject.Object", "Atk.Component"]


def test_hierarchy():
    from pgi.repository import GObject

    repo = Repository("Atk", "1.0")
    Atk = repo.import_module()
    hier = get_hierarchy([Atk.NoOpObjectFactory])
    assert list(hier.keys()) == [GObject.Object]
    assert list(hier[GObject.Object].keys()) == [Atk.ObjectFactory]
    assert list(hier[GObject.Object][Atk.ObjectFactory].keys()) == [Atk.NoOpObjectFactory]
    assert not hier[GObject.Object][Atk.ObjectFactory][Atk.NoOpObjectFactory]


def test_pango():
    repo = Repository("Pango", "1.0")
    mod = repo.parse()
    func = find(mod.functions, "extents_to_pixels")
    assert ":param inclusive:" in func.signature_desc

    func = find(mod.functions, "break_")
    assert ":param text:" in func.signature_desc

    func = find(find(mod.structures, "TabArray").methods, "new")
    assert ":param initial_size:" in func.signature_desc

    assert repo.is_private("Pango.RendererPrivate")
    assert not repo.is_private("Pango.AttrIterator")


def test_glib():
    repo = Repository("GLib", "2.0")
    mod = repo.parse()

    klass = find(mod.pyclasses, "Error")

    # GLib.io_add_watch points to g_io_add_watch_full and should
    # also use its docs
    func = find(mod.functions, "io_add_watch")
    assert ":param priority:" in func.signature_desc

    # we include a note containing the shadowed docs
    assert func.info.shadowed_desc

    assert repo.get_shadowed("g_idle_add") == "g_idle_add_full"

    assert repo.lookup_py_id("g_idle_add") == "GLib.idle_add"
    assert repo.lookup_py_id("g_idle_add", shadowed=False) is None

    klass = find(mod.enums, "BookmarkFileError")
    assert klass.base == "GLib.Enum"

    klass = find(mod.enums, "Enum")
    assert klass.base is None

    klass = find(mod.flags, "FileTest")
    assert klass.base == "GLib.Flags"

    klass = find(mod.flags, "Flags")
    assert klass.base is None

    struct = find(mod.structures, "MemVTable")
    field = find(struct.fields, "realloc")
    assert "object" in field.type_desc


def test_gio():
    repo = Repository("Gio", "2.0")
    Gio = repo.import_module()

    klass = Class.from_object(repo, Gio.Application)
    method = find(klass.methods, "activate")
    signal = find(klass.signals, "activate")

    assert method.info.desc
    assert signal.info.desc
    assert method.info.desc != signal.info.desc

    signal = find(klass.signals, "command_line")
    assert ":param command_line:" in signal.signature_desc

    klass = Class.from_object(repo, Gio.File)
    method = find(klass.methods, "load_contents_finish")
    assert ":returns:" in method.signature_desc


@pytest.mark.xfail(reason="Currently no overrides")
def test_gtk_overrides():
    repo = Repository("Gtk", "3.0")
    Gtk = repo.import_module()
    assert Gtk.get_major_version() == 3

    PyClass.from_object(repo, Gtk.TreeModelRow)
    PyClass.from_object(repo, Gtk.TreeModelRowIter)

    func = Function.from_object("Gtk.Container", "child_get", Gtk.Container.child_get, repo, Gtk.Container)
    assert func.info.desc == "Returns a list of child property values for the given names."
    assert func.signature == "(child, *prop_names)"

    func = Function.from_object("Gtk", "stock_lookup", Gtk.stock_lookup, repo, Gtk)
    assert func.signature == "(stock_id)"

    klass = Class.from_object(repo, Gtk.Widget)
    assert klass.subclasses.count("Gtk.Container") == 1


def test_gtk():
    repo = Repository("Gtk", "3.0")
    Gtk = repo.import_module()

    klass = Class.from_object(repo, Gtk.TreeModel)
    vfunc = find(klass.vfuncs, "do_get_iter")
    assert vfunc.info.desc

    Class.from_object(repo, Gtk.Button)
    Class.from_object(repo, Gtk.Paned)
    Class.from_object(repo, Gtk.ActionBar)

    klass = Class.from_object(repo, Gtk.TextView)
    assert klass.image_path

    klass = Class.from_object(repo, Gtk.Widget)
    translate_coordinates = find(klass.methods, "translate_coordinates")
    # make sure we replace src_widget with self
    assert "src_widget" not in translate_coordinates.info.desc

    mod = repo.parse()
    find(mod.class_structures, "WidgetClass")
    find(mod.structures, "TableChild")
    with pytest.raises(LookupError):
        find(mod.class_structures, "TableChild")
    with pytest.raises(LookupError):
        find(mod.structures, "WidgetClass")


def test_gobject():
    repo = Repository("GObject", "2.0")
    GObject = repo.import_module()
    mod = repo.parse()

    assert repo.lookup_py_id_for_type_struct("GObjectClass") == "GObject.Object"

    klass = Class.from_object(repo, GObject.Object)
    method = find(klass.methods, "list_properties")
    assert method.is_static
    assert method.fullname == "GObject.Object.list_properties"

    klass = find(mod.enums, "GEnum")
    assert klass.base == "GLib.Enum"

    klass = find(mod.flags, "GFlags")
    assert klass.base == "GLib.Flags"

    klass = find(mod.flags, "ParamFlags")
    assert klass.base == "GLib.Flags"


def test_atk():
    repo = Repository("Atk", "1.0")
    Atk = repo.import_module()

    c = Constant.from_object(repo, "", "FOO", Atk.Document.__gtype__)
    assert str(c.value) == "<GType AtkDocument>"

    klass = Class.from_object(repo, Atk.Document)
    method = find(klass.methods, "get_attributes")
    assert method.info.version_added == "1.12"

    method = find(klass.methods, "get_attribute_value")
    assert method.info.version_added == "1.12"

    klass = Class.from_object(repo, Atk.Hyperlink)

    method = find(klass.methods, "is_selected_link")
    assert method.info.deprecated
    assert method.info.version_added == "1.4"
    assert method.info.version_deprecated == "1.8"
    assert method.info.deprecation_desc, "1.8"

    klass = Flags.from_object(repo, Atk.Role)
    info = find(klass.values, "APPLICATION").info
    assert info.version_added == "1.1.4"
