#!/bin/bash

# Init our virtualenv
source venv/bin/activate

# Make sure we'll fail loudly, then install deps
set -xe
pip install -q -e .

# Set up our app and go!
FLASK_APP=tinyvirt flask run
