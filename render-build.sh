#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
