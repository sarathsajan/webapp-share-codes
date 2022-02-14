# Import core libraries
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, session

# Import helper libraries and environment variables
#from users import User
import _functions
import data
share_codes_data = data.Data()
from env_vars.env_vars import ENV_VARS
ENV_VARIABLES = ENV_VARS()

# Import and initialise the Google Cloud Firestore database
import gcfsDB

# Import libraries for Google Sign-in and session creation/management/deletion
import g_auth_session

# Initialise Flask app
app = Flask(__name__)
app.secret_key = ENV_VARIABLES["FLASK_SECRET_KEY"]

# Check if user is logged-in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('authentication'))
    return wrap


@app.route("/")
def index():
    rand_img_fh5 = _functions.get_random_image("fh5")
    rand_img_fh4 = _functions.get_random_image("fh4")
    return render_template('home.html', rand_img_fh5=rand_img_fh5, rand_img_fh4=rand_img_fh4)

@app.route("/explore")
def explore():
    return render_template("explore.html", share_codes_data=share_codes_data) # show top picks of the day, week, month, all-time

@app.route("/search")
def search():
    return render_template("search.html") # basically a form that has all the input fields like in the game

@app.route("/results")
def results():
    return render_template("results.html", share_codes_data="dummy_data")

@app.route("/view/<game_name>/<int:share_code>")
def view_single_share_code(game_name, share_code):
    single_share_code = gcfsDB.get_single_share_code_data(game_name=game_name, share_code=share_code)
    return render_template('view_share_code.html', share_codes_data=single_share_code)

@app.route("/submit")
@is_logged_in
def submit():
    return render_template('submit.html')

@app.route("/authentication")
def authentication():
    return render_template("auth.html")

@app.route("/login")
def login():
    request_uri = g_auth_session.login_with_google(request)
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    user_data = g_auth_session.start_google_authentication(request, code)

    if not user_data['msg']:
        return ('Google Authentication Error')
    
    # Doesn't exist? Add it to the database.
    if not gcfsDB.if_user_data_exists_gcfsDB(user_data):
        gcfsDB.set_user_data_gcfsDB(user_data)

    # Begin user session by logging the user in
    session['logged_in'] = True
    session['user_data'] = user_data
    
    # Send user to profile page
    return redirect(url_for("profile_myself"))

@app.route("/profile/myself")
@is_logged_in
def profile_myself():
    return render_template('profile.html')


@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for("authentication"))


@app.route("/about")
@is_logged_in
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
