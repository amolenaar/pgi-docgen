# Copyright 2016 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

import os
import xml.etree.ElementTree as etree

from .util import get_doap_path


class ProjectSummary(object):

    name = None
    description = None
    homepage = None
    bugtracker = None
    repositories = []
    mailinglists = []
    dependencies = []


def get_project_summary(namespace, version):
    """Returns a summary extracted from a doap file"""

    ps = ProjectSummary()

    doap_path = get_doap_path(namespace)
    if os.path.exists(doap_path):

        with open(doap_path, "rb") as h:
            data = h.read()
            data = data.replace(b"&excl;", b"&#x21;")
            root = etree.fromstring(data)

        # strip namespaces
        for x in root.iter():
            x.tag = x.tag.rsplit("}")[-1]
            for key, value in list(x.attrib.items()):
                del x.attrib[key]
                x.attrib[key.rsplit("}")[-1]] = value

        name = root.find("name")
        shortdesc = root.find("shortdesc")
        description = root.find("description")
        mailing_lists = root.findall("mailing-list")
        homepage = root.find("homepage")
        bug_database = root.find("bug-database")
        repository = root.find("repository")
        if repository is not None:
            repositories = repository.findall(".//browse")
        else:
            repositories = []

        if name is not None:
            ps.name = name.text
            if shortdesc is not None:
                ps.name += " (%s)" % shortdesc.text.strip()

        if description is not None:
            ps.description = description.text

        if homepage is not None:
            ps.homepage = homepage.attrib["resource"]

        if bug_database is not None:
            ps.bugtracker = bug_database.attrib["resource"]

        ps.repositories = [
            (r.attrib["resource"], r.attrib["resource"]) for r in repositories]

        def strip_mailto(s):
            if s.startswith("mailto:"):
                return s[7:]
            return s

        ps.mailinglists = []
        for r in mailing_lists:
            ps.mailinglists.append(
                (strip_mailto(r.attrib["resource"]), r.attrib["resource"])
            )

    return ps
