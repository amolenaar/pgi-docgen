# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

from pgidocgen.funcsig import FuncSignature, arg_to_class_ref, py_type_to_class_ref
from pgidocgen.util import escape_rest


def test_py_type_to_class_ref():
    assert py_type_to_class_ref(str) == ":obj:`str`"


def test_from_string():
    sig = FuncSignature.from_string("foo", "foo(bar: int)")
    assert sig
    assert sig.name == "foo"
    assert sig.args == [["bar", "int"]]
    assert sig.res == []
    assert not sig.raises


def test_from_string_res():
    sig = FuncSignature.from_string("foo", "foo() -> int")
    assert sig.res == [["int"]]


def test_from_string_2():
    sig = FuncSignature.from_string("init", "init(argv: [str] or None) -> argv: [str]")
    assert sig
    assert sig.name == "init"
    assert sig.args == [["argv", "[str] or None"]]
    assert sig.res == [["argv", "[str]"]]
    assert not sig.raises


def test_from_string_args():
    sig = FuncSignature.from_string("init", "init(foo: bool, *args: int)")
    assert sig
    assert sig.name == "init"
    assert not sig.raises
    assert sig.args == [["foo", "bool"], ["*args", "int"]]


def test_from_string_notype():
    sig = FuncSignature.from_string("init", "init(foo)")
    assert sig.args == [["foo", ""]]


def test_from_string_raises():
    sig = FuncSignature.from_string("init", "init(foo)")
    assert not sig.raises

    sig = FuncSignature.from_string("init", "init(foo) raises")
    assert sig.raises


def test_from_string_hash():
    sig = FuncSignature.from_string(
        "to_hash",
        "to_hash(flags: NetworkManager.SettingHashFlags) -> " "{str: {int: int}}",
    )

    assert sig.res == [["{str: {int: int}}"]]

    sig = FuncSignature.from_string(
        "do_get_item_attributes",
        "do_get_item_attributes(item_index: int) -> " "attributes: {str: GLib.Variant}",
    )

    assert sig.res == [["attributes", "{str: GLib.Variant}"]]


def test_to_simple_sig():
    sig = FuncSignature.from_string(
        "to_hash",
        "to_hash(flags: NetworkManager.SettingHashFlags, foo: [int]) -> " "{str: {int: int}}",
    )
    assert sig.to_simple_signature() == "(flags, foo)"


def test_to_simple_sig_2():
    sig = FuncSignature.from_string("to_hash", "to_hash(flags: Foo.Bar, foo: [int or None], *data)")
    assert sig.to_simple_signature() == "(flags, foo, *data)"


def test_arg_to_class_ref():
    assert arg_to_class_ref("bytes") == ":obj:`bytes <str>`"
    assert arg_to_class_ref("int") == ":obj:`int`"
    assert arg_to_class_ref("[int]") == "[:obj:`int`]"
    assert arg_to_class_ref("[Gtk.Window]") == "[:obj:`Gtk.Window`]"
    assert arg_to_class_ref("{Gtk.Window or None: int}") == "{:obj:`Gtk.Window` or :obj:`None`: :obj:`int`}"
    assert arg_to_class_ref("[str] or None") == "[:obj:`str`] or :obj:`None`"
    assert arg_to_class_ref("") == ""


def test_to_rest_listing():
    class FakeRepo(object):
        def lookup_docs(self, type_, name, *args, **kwargs):
            if "para" in type_:
                return escape_rest("PARADOC(%s)" % name), ""
            return escape_rest("RETURNDOC(%s)" % name), ""

    sig = FuncSignature.from_string("go", "go(*args)")
    doc = sig.to_rest_listing(FakeRepo(), "Foo.bar.go")
    # no empty reST references
    assert "``" not in doc

    sig = FuncSignature.from_string("go", "go(a_: [str]) -> int, b_: [str]")
    doc = sig.to_rest_listing(FakeRepo(), "Foo.bar.go")
    assert (
        doc
        == """\
:param a_:
    PARADOC(Foo.bar.go.a\\_)
:type a_: [:obj:`str`]

:returns:
    RETURNDOC(Foo.bar.go)
    \n\
    :b_:
        PARADOC(Foo.bar.go.b\\_)

:rtype: (:obj:`int`, **b_**: [:obj:`str`])\
"""
    )

    sig = FuncSignature.from_string("go", "go(*args: int)")
    doc = sig.to_rest_listing(FakeRepo(), "Foo.bar.go")
    assert (
        doc
        == """\
:param args:
    PARADOC(Foo.bar.go.args)
:type args: :obj:`int`
"""
    )

    # only one out param
    sig = FuncSignature.from_string("go", "go() -> foo: int")
    doc = sig.to_rest_listing(FakeRepo(), "Foo.bar.go")
    assert (
        doc
        == """\
:returns:
    PARADOC(Foo.bar.go.foo)

:rtype: **foo**: :obj:`int`\
"""
    )
