FROM fedora:36

ENV LANG C.UTF-8

RUN dnf install -y gcc gtk4-devel libadwaita-devel cairo-devel cairo-gobject-devel \
    gobject-introspection-devel python3-devel python3-pip \
    git libxml2 graphviz

RUN pip3 install --upgrade \
    "git+https://github.com/pygobject/pgi.git" \
    requests==2.28.0 \
    sphinx==5.0.2 \
    cairocffi==1.3.0 \
    beautifulsoup4==4.11.1 \
    lxml==4.9.0 \
    pytest \
    flake8 \
    coverage \
    pytest-cov

# Fix compatibility issues for GTK 4
RUN rm /usr/local/lib/python3.10/site-packages/pgi/overrides/Gdk.py /usr/local/lib/python3.10/site-packages/pgi/overrides/Gtk.py

WORKDIR /home/user/app
