#!/bin/bash

set -e

TAG="lazka/pgi-docgen:v4"

docker run --security-opt label=disable \
    --rm  --volume "$(pwd)/..:/home/user/app" \
    -t "${TAG}" xvfb-run -a ./pgi-docgen create _docs Gtk-4.0

docker run --security-opt label=disable \
    --rm  --volume "$(pwd)/..:/home/user/app" \
    -t "${TAG}" ./pgi-docgen build _docs _docs/_build
