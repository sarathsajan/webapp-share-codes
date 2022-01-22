from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('home.html')

@app.route("/find")
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
