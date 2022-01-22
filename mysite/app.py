from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return("Forza Horizon share-codes")

app.run(debug=True)