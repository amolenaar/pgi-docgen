#!/bin/bash

set -e

TAG="lazka/pgi-docgen:v4"

podman run --security-opt label=disable \
    --rm  --volume "$(pwd)/..:/home/user/app:Z" \
    --tty --interactive "${TAG}" bash
