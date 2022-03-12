# Import core libraries
import datetime
from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from wtforms import Form, validators, StringField, TextAreaField, SelectField, IntegerField
import json

# Import helper libraries and environment variables
import _functions
import data
share_codes_data = data.Data()
from env_vars.env_vars import ENV_VARS
ENV_VARIABLES = ENV_VARS()

# Import and initialise the Google Cloud Firestore database
import gcfsDB

# Import libraries for Google Sign-in and creation/management/deletion of session
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

# Create a Search Form using WTForms
class SearchForm(Form):
    game = SelectField('Game', choices=[(False, 'Select'), ('forza_horizon_4', 'Forza Horizon 4'), ('forza_horizon_5', 'Forza Horizon 5')], validators=[validators.DataRequired()])
    share_code_type = SelectField('Share code type', choices=[(False, 'Select'), ('event_lab', 'Event Lab'), ('vinyl_group', 'Vinyl Group'), ('livery_design', 'Livery Design')], validators=[validators.DataRequired()])
    event_lab_season = SelectField('Season', choices=[('all', 'All'), ('hot', 'Hot'), ('wet', 'Wet'), ('storm', 'Storm'), ('dry', 'Dry')], validators=[validators.Optional()])
    event_lab_racing_series = SelectField('Racing Series', choices=[('all', 'All'), ('road', 'Road'), ('dirt', 'Dirt'), ('cross_country', 'Cross Country'), ('drag', 'Drag')], validators=[validators.Optional()])
    search_description = TextAreaField('Description will help in getting relevant results', validators=[validators.InputRequired(), validators.Length(min=10, max=300)])

@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        search_query = {
            'game' : form.game.data,
            'share_code_type' : form.share_code_type.data,
            'event_lab_season' : form.event_lab_season.data if form.share_code_type.data == 'event_lab' else None,
            'event_lab_racing_series' : form.event_lab_racing_series.data if form.share_code_type.data == 'event_lab' else None,
            'search_description': form.search_description.data.replace('.', ' ').split()
        }
        search_query = json.dumps(search_query)
        return redirect(url_for("results", search_query=search_query))
    return render_template("search.html", form=form) # basically a form that has all the input fields like in the game

@app.route("/results")
def results():
    search_query = request.args.get('search_query')
    search_query = json.loads(search_query)
    search_results = gcfsDB.get_search_results(search_query)
    return render_template("results.html", search_query=search_query, search_results=search_results)

@app.route("/view/<game>/<int:share_code>")
def view_single_share_code(game, share_code):
    single_share_code = gcfsDB.get_single_share_code_data(game=game, share_code=share_code)
    print(single_share_code)
    return render_template('view_share_code.html', share_codes_data=single_share_code),

# Create a Submission Form using WTForms
class SubmissionForm(Form):
    share_code = IntegerField('Share code', validators=[validators.InputRequired(), validators.NumberRange(min=100000000, max=999999999)])
    title  = StringField('Title', validators=[validators.InputRequired(), validators.Length(min=5, max=50)])
    game = SelectField('Game', choices=[(False, 'Select'), ('forza_horizon_4', 'Forza Horizon 4'), ('forza_horizon_5', 'Forza Horizon 5')], validators=[validators.DataRequired()])
    share_code_type = SelectField('Share code type', choices=[(False, 'Select'), ('event_lab', 'Event Lab'), ('vinyl_group', 'Vinyl Group'), ('livery_design', 'Livery Design')], validators=[validators.DataRequired()])
    event_lab_season = SelectField('Season', choices=[('all', 'All'), ('hot', 'Hot'), ('wet', 'Wet'), ('storm', 'Storm'), ('dry', 'Dry')], validators=[validators.Optional()])
    event_lab_racing_series = SelectField('Racing Series', choices=[('all', 'All'), ('road', 'Road'), ('dirt', 'Dirt'), ('cross_country', 'Cross Country'), ('drag', 'Drag')], validators=[validators.Optional()])
    preview_img_url = StringField('Preview Image URL', validators=[validators.Optional(), validators.Length(max=600)])
    yt_video_url = StringField('YouTube Video URL', validators=[validators.Optional(), validators.Length(max=100)])
    description = TextAreaField('Tell why would people enjoy your share code', validators=[validators.InputRequired(), validators.Length(min=10, max=300)])

@app.route("/submit", methods=['GET', 'POST'])
@is_logged_in
def submit():
    form = SubmissionForm(request.form)
    if request.method == 'POST' and form.validate():
        share_code_candidate = {
            'share_code' : form.share_code.data,
            'title' : form.title.data,
            'game' : form.game.data,
            'share_code_type' : form.share_code_type.data,
            'event_lab_season' : form.event_lab_season.data if form.share_code_type.data == 'event_lab' else None,
            'event_lab_racing_series' : form.event_lab_racing_series.data if form.share_code_type.data == 'event_lab' else None, 
            'preview_img_url' : form.preview_img_url.data,
            'embed_yt_url' : form.yt_video_url.data,
            'description' : form.description.data,
            'author': session['user_data']['users_name'],
            'date': datetime.datetime.now(),
        }
        submit_flag = gcfsDB.check_and_add_share_code_gcfsDB(share_code_candidate)
        if submit_flag == 'exists':
            flash('That share code already exists', category='danger')
            return redirect(url_for('submit'))
        else:
            flash('Your share code has been added', category='success')
            return redirect(url_for("profile_myself"))
    return render_template('submit.html', form=form)

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
