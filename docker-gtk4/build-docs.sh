#!/bin/bash

set -e

TAG="lazka/pgi-docgen:v4"

podman run --security-opt label=disable \
    --rm  --volume "$(pwd)/..:/home/user/app" \
    -t "${TAG}" ./pgi-docgen create _docs Gtk-4.0 Adw-1

podman run --security-opt label=disable \
    --rm  --volume "$(pwd)/..:/home/user/app" \
    -t "${TAG}" ./pgi-docgen build _docs _docs/_build
