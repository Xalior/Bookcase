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

videostream = None
videourl = None

feed = []


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid username and password pair...'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            update_feed()
            return redirect(url_for('list_all'))
    return render_template('login.html', error=error)


def check_feed():
    if len(feed) == 0:
        update_feed()


def check_nologin():
    return session.get('logged_in')


def check_login():
    return not check_nologin()


schedule_payload()

@app.route('/admin')
def list_all():
    if check_login():
        return redirect(url_for('login'))

    check_feed()

    return render_template('list_all.html', feed=feed)


@app.route('/edit/<id>')
def edit(id):
    offset = None
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    check_feed()
    ep = feed[int(id)]

    get_video(ep.enclosure)

    if not offset:
        offset = app.config['THUMB_LAG']

    return render_template('edit.html', ep=ep, offset=offset, config=app.config, rand=random.random())


@app.route('/preview/<id>/at/<seconds>.jpg')
def preview(id, seconds):
    id = int(id)
    seconds = float(seconds)

    if not session.get('logged_in'):
        redirect(url_for('login'))

    check_feed()
    ep = feed[id]

    get_video(ep.enclosure)

    videoframe = videostream.get_frame_at_sec(seconds)
    return send_image(videoframe.image())


@app.route('/update/<id>/to/<seconds>')
def update(id, seconds):
    if not session.get('logged_in'):
        redirect(url_for('login'))

    id = int(id)
    seconds = float(seconds)

    check_feed()
    ep = feed[id]

    get_video(ep.enclosure)

    videoframe = videostream.get_frame_at_sec(seconds)
    videoframe.image().save(root_dir()+app.config['THUMB_DIR']+ep.baseName+".jpg")
    return redirect(url_for('edit', id=id))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_resource(path):  # pragma: no cover
    mimetypes = {
        ".js": "application/javascript",
        ".css": "text/css",
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".gif": "text/gif",
        ".html": "text/html",
    }
    complete_path = os.path.join(root_dir(), path)
    ext = os.path.splitext(path)[1]
    mimetype = mimetypes.get(ext, "text/html")
    content = get_file(complete_path)
    return Response(content, mimetype=mimetype)


@app.route('/admin/<path>/<key>')
def cron(path, key):
    if (path == app.config['CRON_PATH']) and (key == app.config['CRON_KEY']):
        schedule_payload()
        abort(404, 'done')
    abort(403, 'gone')


if __name__ == "__main__":
    app.run()
