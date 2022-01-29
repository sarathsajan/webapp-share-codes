from __future__ import unicode_literals
from flask import Flask, render_template
import os
import random

import _functions
import data
share_codes_data = data.Data()

app = Flask(__name__)


@app.route("/")
def index():
    rand_img_fh5 = _functions.get_random_image("fh5")
    rand_img_fh4 = _functions.get_random_image("fh4")
    return render_template('home.html', rand_img_fh5=rand_img_fh5, rand_img_fh4=rand_img_fh4)

@app.route("/explore")
def explore():
    return render_template("explore.html", share_codes_data=share_codes_data)

@app.route("/search")
def search():
    return ("share-code search form")

@app.route("/submit")
def submit():
    return ("share-code submission form")

@app.route("/code/<string:unique_id>")
def code(unique_id):
    return render_template("code.html", share_codes_data=share_codes_data, unique_id=unique_id)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True)
