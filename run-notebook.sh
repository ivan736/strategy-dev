#!/bin/bash

subuidSize=$(( $(podman info --format "{{ range .Host.IDMappings.UIDMap }}+{{.Size }}{{end }}" ) - 1 ))
subgidSize=$(( $(podman info --format "{{ range .Host.IDMappings.GIDMap }}+{{.Size }}{{end }}" ) - 1 ))
uid=1000
gid=100

podman run -it -p 8888:8888 \
    --name notebook \
    -e GRANT_SUDO=yes \
    -e JUPYTER_TOKEN=ivan123 \
    -v "$(pwd)/notebook-vol:/home/jovyan/codes" -u root \
    --uidmap $uid:0:1 --uidmap 0:1:$uid \
    --gidmap $gid:0:1 --gidmap 0:1:$gid \
    jupyter/scipy-notebook