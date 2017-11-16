#!/bin/bash

# Init our virtualenv
source venv/bin/activate

# Make sure we'll fail loudly, then install deps
set -xe
pip install -q -e .

# './run.sh debug' => Flask debugger enabled!
if [[ ${1,,} == debug* ]]; then
	export FLASK_DEBUG=1
else
	export FLASK_DEBUG=0
fi

# Set up our app and go!
export FLASK_APP=tinyvirt
flask run --host=0.0.0.0 --port=5000
