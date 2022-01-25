from flask import Flask, render_template
import os
import random

app = Flask(__name__)


@app.route("/")
def index():
    rand_img_fh5 = str(random.randint(1, len([name for name in os.listdir('./static/images/fh5/')])))
    print(rand_img_fh5)
    rand_img_fh5 = rand_img_fh5 + '_' + rand_img_fh5 + '_11zon.jpeg'
    rand_img_fh4 = str(random.randint(1, len([name for name in os.listdir('static/images/fh4/')])))
    rand_img_fh4 = rand_img_fh4 + '_' + rand_img_fh4 + '_11zon.jpeg'
    return render_template('home.html', rand_img_fh5 = rand_img_fh5, rand_img_fh4 = rand_img_fh4)

@app.route("/explore")
def explore():
    return ("<p>find share-codes by time 1 day, 1 week, 1 month etc</p><br>\
            <p>find share-codes by category like routes, livery, tune etc</p><br>\
            <p>find share-codes by popularity like top, rising, hot, trending etc</p>")

@app.route("/search")
def search():
    return ("share-code search form")

@app.route("/submit")
def submit():
    return ("share-code submission form")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True)
