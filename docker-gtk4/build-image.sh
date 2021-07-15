#!/bin/bash

set -e

TAG="lazka/pgi-docgen:v4"

podman build --tag "${TAG}" --file "Dockerfile" ..
