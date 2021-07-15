FROM fedora:34

ENV LANG C.UTF-8

RUN yum install -y gcc gtk4-devel cairo-devel cairo-gobject-devel gobject-introspection-devel python3-devel python3-pip xorg-x11-server-Xvfb \
    git python3-lxml graphviz

RUN pip3 install --upgrade \
    "git+https://github.com/pygobject/pgi.git" \
    requests==2.22.0 \
    jinja2==2.10.1 \
    sphinx==1.8.5 \
    cairocffi==1.0.2 \
    beautifulsoup4==4.7.1 \
    pytest \
    flake8 \
    coverage \
    pytest-cov

# Fix compatibility issues for GTK 4
RUN rm /usr/local/lib/python3.9/site-packages/pgi/overrides/Gdk.py /usr/local/lib/python3.9/site-packages/pgi/overrides/Gtk.py

WORKDIR /home/user/app
