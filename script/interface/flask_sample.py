#!/usr/bin/env python3
# coding: utf-8

from flask import Flask
app = Flask(__name__, static_folder='.', static_url_path='')
@app.route('/')
def index():
    return app.send_static_file('templates/index.html')


app.run(port=8000, debug=True)
