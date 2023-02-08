#!/bin/env sh

# install src packages
pip install --no-deps -e /src/model2queue

# run jupyter
jupyter-lab --ip=0.0.0.0 --allow-root --no-browser
