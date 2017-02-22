"""ReviewGenius"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from indexes import INDEXES
from model import Product, Review, User, Category, connect_to_db, db
from sqlalchemy import desc
from product_genius import find_products, get_scores, get_chart_data, find_reviews

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ProductGenius"

# Jinja2 should raise error if it encounters an undefined variable
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def display_homepage():
    """Display Homepage."""

    return render_template("homepage.html",
                           indexes=INDEXES)


@app.route('/search')
def search_products():
    """Retrieve data from search form and display product results page."""

    search_query = request.args.get('query')
    search_index = request.args.get('index')

    # Retrieve products from db that match search_query within search_index
    products = find_products(search_query, search_index)

    if len(products) > 0:
        return render_template("product_listing.html",
                               products=products)
    else:
        return render_template("no_products.html")


@app.route('/product-scores/<asin>.json')
def product_reviews_data(asin):
    """Return data about product reviews for histogram."""

    score_list = get_scores(asin)
    data_dict = get_chart_data(score_list)

    return jsonify(data_dict)


@app.route('/search-review/<asin>.json')
def search_reviews(asin):
    """Perform full-text search within product reviews.
       Returns the matching reviews via json to the front end.
    """

    search_query = request.args.get('query')

    # Run full-text search within a product's reviews
    # Returns a list of review tuples.
    reviews = find_reviews(asin, search_query)

    # Reformat review tuples into a dictionary
    reviews_dict = {}

    for rev in reviews:
        reviews_dict[rev[0]] = {
            "reviewer_name": rev[2],
            "review": rev[3],
            "summary": rev[8],
            "score": rev[7],
            "time": rev[9]
        }

    return jsonify(reviews_dict)


@app.route('/product/<asin>')
def display_product_profile(asin):
    """Display a product details page.

       Should have a pretty histogram with scores, a product rating
       built from bayesian logic, the product's reviews, a search bar for
       reviews (that returns w/ ajax), and a form to favorite the product.
    """

    product = Product.query.filter_by(asin=asin).one()
    reviews = Review.query.filter_by(asin=asin).order_by(desc(Review.score)).all()

    return render_template("product_details.html",
                           product=product,
                           reviews=reviews)


##################### Favorites ################################

@app.route('/user/int<user_id>')
def display_user_profile():
    """Display user's favorite products and reviews.

       User should be able to compare products/reviews side by side.
       Might add functionality to add to the amazon cart via their API
    """

    pass


@app.route('/favorite-product', methods=['POST'])
def add_favorite_product():
    """Adds a product to a user's favorites"""

    asin = request.form.get('asin')

    flash("Product added to favorites")

    return redirect(url_for('.display_product_profile', asin=asin))


@app.route('/favorite-review', methods=['POST'])
def add_favorite_review():
    """Adds a review for a product to a user's favorites"""

    pass



################# Login, logout, and registration ###############

@app.route('/register')
def register_user():
    """Registers a new user"""

    pass


@app.route('/login')
def login():
    """Logs a registered user into the app"""

    pass


@app.route('/logout')
def logout():
    """Logs a registered user out of the app"""

    pass



##################################################################

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
