from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('home.html')

@app.route("/explore")
def submit():
    return ("top 5 share-code of past 1 day, 1 week, 1 month for each category like routes, livery, tune etc")

@app.route("/search")
def submit():
    return ("share-code search form")

@app.route("/submit")
def submit():
    return ("share-code submission form")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True)
