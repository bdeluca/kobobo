#!/usr/bin/env bash
set -e

j2 /app/config/settings.j2 -o /app/config/settings.ini



exec "$@"