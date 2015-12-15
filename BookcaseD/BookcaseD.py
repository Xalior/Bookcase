#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Custom Python server for D's Digital Bookcase
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2015 by D. Rimron-Soutter
    :license: BSD, see LICENSE for more details.
"""

import os, logging, re, json, time, datetime, StringIO, platform, random
from flask import Flask, request, session, redirect, url_for, flash, \
     render_template, Response, send_file, abort
import ttyrelay, ledarray

class GenericObject(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def root_dir():
    return os.path.abspath(os.path.dirname(__file__)+"/server")

def get_file(filename):
    try:
        src = os.path.join(root_dir(), filename)
        return open(src).read()
    except IOError as exc:
        return str(exc)

# create our little application :)
app = Flask(__name__, static_url_path='', static_folder=root_dir())

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='BookcaseD',
    USERNAME='htpc',
    PASSWORD='Password',
    # App Specific Settings...
    DEBUG=True
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

if app.config['DEBUG']:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
else:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

hvac = ttyrelay.TTYRelay(0)

print hvac.status
hvac.demo()

videostream = None
videourl = None

frame = []


@app.route('/set/<id>/to/<r>/<g>/<b>')
def update(id, r, g, b):
    print(r, g, b)
    return redirect(url_for('', id=id))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_resource(path):  # pragma: no cover
    mimetypes = {
        ".js": "application/javascript",
        ".css": "text/css",
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".gif": "text/gif",
        ".html": "text/html"
    }
    complete_path = os.path.join(root_dir(), path)
    ext = os.path.splitext(path)[1]
    mimetype = mimetypes.get(ext, "text/html")
    content = get_file(complete_path)
    return Response(content, mimetype=mimetype)

if __name__ == "__main__":
    app.run()
