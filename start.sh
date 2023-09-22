#!/usr/bin/env sh
gunicorn bot:app -b :8081 --reload