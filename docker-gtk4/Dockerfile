FROM fedora:34

ENV LANG C.UTF-8

RUN yum install -y gcc gtk4-devel cairo-devel cairo-gobject-devel gobject-introspection-devel python3-devel python3-pip xorg-x11-server-Xvfb \
    git python3-lxml graphviz


ARG HOST_USER_ID=5555
ENV HOST_USER_ID ${HOST_USER_ID}
RUN useradd -u $HOST_USER_ID -ms /bin/bash user
RUN echo 'user ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER user

ENV PATH="/home/user/.local/bin:${PATH}"

RUN pip3 install --user --upgrade \
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

WORKDIR /home/user
COPY --chown=user:user . ./install
WORKDIR /home/user/install

ENV PYTHONPATH /home/user/install
# RUN ./pgi-docgen create-debian --install --no-build _docs

# Fix compatibility issues for GTK 4
RUN rm /home/user/.local/lib/python3.9/site-packages/pgi/overrides/Gdk.py /home/user/.local/lib/python3.9/site-packages/pgi/overrides/Gtk.py

# ENV PGI_DOCGEN_DEBIAN_DATA_DIR /home/user/install/_debian_build_cache

WORKDIR /home/user/app
