#!/usr/bin/env bash
set -o errexit

# Always upgrade the packaging toolchain first
python -m pip install --upgrade pip setuptools wheel

# Force wheels for pydantic/pydantic-core (no source builds)
# If a compatible wheel exists (it does for Linux x86_64 on Py3.11), this succeeds without Rust.
python -m pip install --only-binary=:all: pydantic==2.8.2 pydantic-core==2.18.4

# Now install the rest
python -m pip install --upgrade -r requirements.txt
