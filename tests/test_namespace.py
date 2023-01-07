# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.


from pgidocgen.namespace import fixup_since, get_cairo_types, get_namespace, get_versions


def test_gtk():
    ns = get_namespace("Gtk", "3.0")
    types = ns.types
    ns.docs

    for key, values in types.items():
        for v in values:
            assert v.startswith("Gtk."), v

    assert types["GtkWindow"] == ["Gtk.Window"]
    assert types["GtkAppChooser"] == ["Gtk.AppChooser"]
    assert types["GtkArrowType"] == ["Gtk.ArrowType"]

    type_structs = ns.type_structs
    assert type_structs["GtkTreeStoreClass"] == "Gtk.TreeStore"

    assert types["gtk_list_store_newv"] == ["Gtk.ListStore.new"]
    assert types["gtk_list_store_new"] == []


def test_gdk():
    ns = get_namespace("Gdk", "3.0")
    types = ns.types
    docs = ns.docs
    versions = get_versions(docs)
    assert "2.0" in versions
    assert "3.0" in versions

    assert types["GdkModifierType"] == ["Gdk.ModifierType"]
    assert ns.instance_params["Gdk.Window.begin_paint_region"] == "window"


def test_gdkpixbuf():
    ns = get_namespace("GdkPixbuf", "2.0")

    assert ns.types["gdk_pixbuf_animation_ref"] == []


def test_gobject():
    ns = get_namespace("GObject", "2.0")
    types = ns.types
    ns.docs

    assert types["GTypeCValue"] == ["GObject.TypeCValue"]
    assert types["GBoxed"] == ["GObject.GBoxed"]

    assert types["G_MAXSSIZE"] == ["GObject.G_MAXSSIZE"]
    assert types["GType"] == ["GObject.GType"]


def test_glib():
    ns = get_namespace("GLib", "2.0")
    types = ns.types
    ns.docs

    assert types["GBookmarkFileError"] == ["GLib.BookmarkFileError"]

    assert types["G_MININT8"] == ["GLib.MININT8"]

    assert types["g_idle_add_full"] == ["GLib.idle_add"]

    # non-introspectable
    assert ns.types["GVariantIter"] == []


def test_atk():
    ns = get_namespace("Atk", "1.0")
    ns.types
    docs = ns.docs
    versions = get_versions(docs)
    assert "ATK-0.7" not in versions
    assert "0.7" in versions
    assert "2.16" in versions


def test_cairo():
    ns = get_namespace("cairo", "1.0")
    types = ns.types
    ns.docs

    assert types["cairo_t"] == ["cairo.Context"]


def test_pycairo():
    types = get_cairo_types()
    assert types["cairo_set_operator"] == ["cairo.Context.set_operator"]

    assert types["cairo_surface_get_content"] == ["cairo.Surface.get_content"]


def test_pango():
    ns = get_namespace("Pango", "1.0")
    types = ns.types
    ns.docs

    assert types["pango_break"] == ["Pango.break_"]


def test_deps():
    ns = get_namespace("DBus", "1.0")
    deps = ns.dependencies
    assert ("GObject", "2.0") in deps

    ns = get_namespace("GLib", "2.0")
    deps = ns.dependencies
    assert not deps

    ns = get_namespace("GObject", "2.0")
    deps = ns.dependencies
    assert deps == [("GLib", "2.0")]


def test_all_deps():
    ns = get_namespace("DBus", "1.0")
    deps = ns.all_dependencies
    assert ("GObject", "2.0") in deps
    assert ("GLib", "2.0") in deps


def test_fixup_added_since():
    assert fixup_since("Foo\nSince: 3.14") == ("Foo", "3.14")
    assert fixup_since("Foo\n(Since: 3.14)") == ("Foo", "3.14")
    assert fixup_since("Foo\n@Since: ATK-3.14") == ("Foo", "3.14")
    assert fixup_since("to the baseline. Since 3.10.") == ("to the baseline.", "3.10")


def test_fixup_deprecated_since():
    assert fixup_since("Since 2.12. Use atk_component_get_extents().") == (
        "Use atk_component_get_extents().",
        "2.12",
    )
