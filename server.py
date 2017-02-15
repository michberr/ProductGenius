from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ReviewGenius"

# Jinja2 should raise error if it encounters an undefined variable
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def display_homepage():
    """Display Homepage."""

    return render_template("homepage.html",
                           indexes=INDEXES)


@app.route('/search')
def search_amazon(query, index):
    """Retrieve data from search form and display product results page."""

    search_index = request.args.get('index')
    query = request.args.get('query')

    # If query is in local database, query database
    if query in Query.query.all():

        # Filter by products containing the query term
        results = Product.query.filter_by()


    # Otherwise make call to amazon api and add information to database
    else:
        results = get_amazon_results(query, search_index)

    return render_template("product_page.html",
                           results)


# @app.route('/user/int<user_id>')
# def display_user_profile():
#     """Display users favorite products and reviews"""

#     return render_template("user_page.html")


# @app.route('/register')

# @app.route('/login')

# @app.route('/logout')


if __name__ == "__main__":

    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')
