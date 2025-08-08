#!/usr/bin/env bash
# Exit if any command fails
set -o errexit

# Upgrade pip, setuptools, and wheel first
pip install --upgrade pip setuptools wheel

# Install dependencies from requirements.txt
pip install -r requirements.txt
