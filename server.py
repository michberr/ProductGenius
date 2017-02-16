"""ReviewGenius"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from indexes import INDEXES
from model import Product, Review, User, connect_to_db, db
import sqlalchemy

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
def search_amazon():
    """Retrieve data from search form and display product results page."""

    search_index = request.args.get('search-index')
    search_query = request.args.get('search-query')

    product_query = Product.query.filter(Product.title.like('%'+search_query+'%'),
                                         Product.n_scores > 5)

    results = product_query.all()

    print results

    # else:
    #     # join load with categories to reduce the search
    #     search_results =

    if product_query.count() > 0:
        return render_template("product_page.html",
                               results=results)
    else:
        return render_template("no_products.html")



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

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.run(port=5000, host='0.0.0.0')
