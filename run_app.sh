#!/usr/bin/env bash
cd "$1" || exit 1
shift
exec "${SHELL:-/bin/bash}" -i -c "$*"
