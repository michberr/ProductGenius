"""ReviewGenius"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from indexes import INDEXES
from model import Product, Review, User, connect_to_db, db
from sqlalchemy import desc

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
def search_products():
    """Retrieve data from search form and display product results page."""

    search_index = request.args.get('index')
    search_query = request.args.get('query')

    product_query = Product.query.filter(Product.title.like('%'+search_query+'%'))

    # Join product query with categories to search within an index
    if search_index != "All":
        product_query.query.filter(Product.categories.in_(search_index))

    if product_query.count() > 0:
        results = product_query.all()
        return render_template("product_page.html",
                               results=results)
    else:
        return render_template("no_products.html")


@app.route('/search-review')
def search_reviews():
    """Search through reviews for a product and display the results"""

    pass


@app.route('/user/int<user_id>')
def display_user_profile():
    """Display user's favorite products and reviews.

       User should be able to compare products/reviews side by side.
       Might add functionality to add to the amazon cart via their API
    """

    pass


@app.route('/product/<asin>')
def display_product_profile(asin):
    """Display a product details page.

       Should have a pretty histogram with scores, an emoji/number
       for wilson's ranking, reviews, a search bar for reviews (that
       returns with an ajax call), and a form to favorite the product.
    """

    product = Product.query.filter_by(asin=asin).one()
    reviews = Review.query.filter_by(asin=asin).order_by(desc(Review.score)).all()

    print product
    print reviews

    return render_template("product_details.html",
                           product=product,
                           reviews=reviews)

##################### Favorites ################################

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
