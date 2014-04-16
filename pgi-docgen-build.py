#!/usr/bin/python
# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

"""
usage: pgi-docgen-build.py [-h] source

Build the sphinx environ created with pgi-docgen

positional arguments:
  source      path to the sphinx environ base dir
"""

import argparse
import os
import subprocess
import multiprocessing


OPTIPNG = "optipng"


def has_optipng():
    try:
        subprocess.check_output([OPTIPNG, "--version"])
    except OSError:
        return False
    return True


def _do_optimize(path):
    subprocess.check_output([OPTIPNG, path])
    return path


def png_optimize_dir(dir_, pool_size=6):
    """Optimizes all pngs in dir_ (non-recursive)"""

    if not os.path.exists(dir_):
        return

    pngs = [e for e in os.listdir(dir_) if e.lower().endswith(".png")]
    paths = [os.path.join(dir_, f) for f in pngs]

    pool = multiprocessing.Pool(pool_size)
    for i, path in enumerate(pool.imap_unordered(_do_optimize, paths), 1):
        name = os.path.basename(path)
        print "%s(%d/%d): %r" % (OPTIPNG, i, len(paths), name)


def do_build(path, build_path):
    sphinx_args = [path, build_path]
    jobs = os.environ.get("JOBS", "")
    if jobs:
        sphinx_args.insert(0, "-j" + jobs)
    subprocess.check_call(["sphinx-build"] + sphinx_args)

    if has_optipng():
        png_dirs = [
            os.path.join(build_path, "_static"),
            os.path.join(build_path, "_images")
        ]

        for dir_ in png_dirs:
            png_optimize_dir(dir_)
    else:
        print "optipng missing, skipping compression"

    print "Done. See file://%s/index.html" % os.path.abspath(build_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Build the sphinx environ created with pgi-docgen')
    parser.add_argument('source', help='path to the sphinx environ base dir')
    args = parser.parse_args()

    to_build = {}

    for entry in os.listdir(args.source):
        if entry.startswith("_"):
            continue
        path = os.path.join(args.source, entry)

        # extract the build dir from the config
        conf_path = os.path.join(path, "_pgi_docgen_conf.py")
        with open(conf_path, "rb") as h:
            exec_env = {}
            exec h.read() in exec_env
        target_path = exec_env["TARGET"]
        deps = set(exec_env["DEPS"])
        build_path = os.path.join(target_path, entry)

        to_build[entry] = (path, build_path, deps)

    if not to_build:
        raise SystemExit("Nothing to build")

    to_ignore = set(["cairo-1.0"])

    # don't build cairo-1.0, we reference the external one
    for ignore in to_ignore:
        to_build.pop(ignore, None)

    try:
        os.mkdir(target_path)
    except OSError:
        pass

    with open(os.path.join(target_path, "index.html"), "wb") as h:
        h.write("""\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Python GI API Reference</title>
  </head>
  <body>
  <ul>""")

        for entry in sorted(to_build.keys()):
            h.write("<li><a href='%s/index.html'>%s</a></li>\n" % (entry, entry))

        h.write("""\
  </ul>
  </body>
</html>
""")

    # build bottom up
    done = set()
    num_to_build = len(to_build)
    while to_build:
        did_build = False
        for entry, (path, build_path, deps) in to_build.items():
            deps.difference_update(done)
            deps.difference_update(to_ignore)
            if not deps:
                did_build = True
                done.add(entry)
                del to_build[entry]

                if os.path.exists(build_path):
                    print "%r exists, skipping" % build_path
                else:
                    print "#" * 80
                    print "# %s: %d of %d" % (
                        entry, len(done), num_to_build)
                    do_build(path, build_path)

        assert did_build, (to_build,)
