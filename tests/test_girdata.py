# Copyright 2015 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

import os
import re

import pytest

from pgidocgen.girdata import (
    Library,
    Project,
    get_class_image_dir,
    get_class_image_path,
    get_docref_dir,
    get_docref_path,
    get_project_summary,
)
from pgidocgen.util import import_namespace


def test_get_project_summary():
    s = get_project_summary("Gtk", "4.0")
    assert s.name == "gtk (Multi-platform toolkit)"
    assert s.description.startswith("GTK is a")
    assert s.homepage
    assert s.bugtracker
    assert s.mailinglists
    assert s.repositories

    get_project_summary("GIRepository", "1.0")
    get_project_summary("GstVideo", "1.0")


def test_get_library_version():
    mods = [
        "Gtk-4.0",
        "Atk-1.0",
        "Gst-1.0",
        "Poppler-0.18",
        "Anthy-9000",
        "InputPad-1.0",
        "Pango-1.0",
        "WebKit2-4.0",
        "GdkPixbuf-2.0",
        "LunarDate-2.0",
        "TotemPlParser-1.0",
        "GVnc-1.0",
    ]

    for m in mods:
        ns, version = m.split("-", 1)
        try:
            import_namespace(ns, version)
        except ImportError:
            continue
        lib = Library.for_namespace(ns, version)
        assert lib.version


def test_get_project_version():
    assert Project.for_namespace("GObject").version == Project.for_namespace("GLib").version


def test_get_tag():
    def get_tag(namespace):
        return Project.for_namespace(namespace).get_tag()

    assert re.match(r"\d+\.\d+\.\d+", get_tag("Gtk"))
    assert re.match(r"ATK_\d+_\d+_\d+", get_tag("Atk"))
    assert re.match(r"\d+\.\d+\.\d+", get_tag("Gst"))
    assert not get_tag("Nope")


def test_get_docref_dir():
    assert os.path.isdir(get_docref_dir())


@pytest.mark.skip(reason="No docref folder for Gtk-4.0")
def test_get_docref_path():
    assert os.path.isfile(get_docref_path("Gtk", "4.0"))


@pytest.mark.skip(reason="No class image folder for Gtk-4.0")
def test_get_class_image_dir():
    assert os.path.isdir(get_class_image_dir("Gtk", "4.0"))


@pytest.mark.skip(reason="No class images for Gtk-4.0")
def test_get_class_image_path():
    assert os.path.isfile(get_class_image_path("Gtk", "4.0", "Window"))


def test_get_source_func():
    def get_url(namespace, path):
        project = Project.for_namespace(namespace)
        func = project.get_source_func(namespace)
        if not func:
            return ""
        return func(path)

    import_namespace("GstApp", "1.0")
    import_namespace("GstAllocators", "1.0")
    import_namespace("GstAudio", "1.0")
    import_namespace("GstPbutils", "1.0")

    url = get_url("Gtk", "gtk/gtktoolshell.c:30")
    assert re.match(
        r"https://gitlab\.gnome\.org/GNOME/gtk/blob/" r"\d+\.\d+\.\d+/gtk/gtktoolshell\.c#L30",
        url,
    )

    url = get_url("Gst", "gst/gstelementfactory.c:430")
    # https://gitlab.freedesktop.org/gstreamer/gstreamer/blob/1.14.4/gst/gstelementfactory.c#L430
    assert re.match(
        r"https://gitlab\.freedesktop\.org/gstreamer/"
        r"gstreamer/blob/\d+\.\d+\.\d+/"
        r"gst/gstelementfactory\.c\#L\d+",
        url,
    ), url
