"""ReviewGenius"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from product_indexes import INDEXES
from model import User, connect_to_db, db
from product_genius import find_products, find_reviews, get_scores, get_chart_data
from product_genius import register_user, update_favorite_review, get_favorite_reviews
from product_genius import format_reviews_to_dicts, update_favorite_product
from product_genius import get_product_by_asin, get_reviews_by_asin, is_favorite_product
import sqlalchemy

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
                               query=search_query,
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

    favorites = set()
    user_id = None

    if "user" in session:
        user_id = session["user"]["id"]
        favorites = get_favorite_reviews(user_id)

    # Converts list of review tuples into a list of dictionaries
    review_dict_list = format_reviews_to_dicts(reviews, user_id, favorites)

    return jsonify(review_dict_list)


@app.route('/product/<asin>')
def display_product_profile(asin):
    """Display a product details page.

       Should have a pretty histogram with scores, a product rating
       built from bayesian logic, the product's reviews, a search bar for
       reviews (that returns w/ ajax), and a heart to favorite the product.
    """

    product = get_product_by_asin(asin)
    reviews = get_reviews_by_asin(asin)

    favorite_reviews = None
    is_favorite = None

    if "user" in session:
        user_id = session["user"]["id"]

        # Return a set of their favorite reviews, and a boolean for whether 
        # they favorited the product on this page
        favorite_reviews = get_favorite_reviews(user_id)
        is_favorite = is_favorite_product(user_id, asin)

    return render_template("product_details.html",
                           product=product,
                           reviews=reviews,
                           is_favorite=is_favorite,
                           favorite_reviews=favorite_reviews)


##################### Favorites ################################

@app.route('/user/int<user_id>')
def display_user_profile():
    """Display user's favorite products and reviews.

       User should be able to compare products/reviews side by side.
       Might add functionality to add to the amazon cart via their API
    """

    pass


@app.route('/favorite-product', methods=['POST'])
def favorite_product():
    """Adds or removes a product from a user's favorites.

       Returns a message of whether the product was favorited or unfavorited.
    """

    asin = request.form.get('asin')
    user_id = session['user']['id']

    # Adds or removes a product from a user's favorites
    favorite_status = update_favorite_product(user_id, asin)

    return favorite_status


@app.route('/favorite-review', methods=['POST'])
def favorite_review():
    """Add or remove a product review from a user's favorites

       Returns a message of whether the review was favorited or unfavorited
    """

    review_id = request.form.get('reviewID')
    user_id = session['user']['id']

    # Adds or removes a product from a user's favorites
    favorite_status = update_favorite_review(user_id, review_id)

    return favorite_status



################# Login, logout, and registration ###############

@app.route('/register', methods=["GET"])
def display_registration():
    """Display register form"""

    return render_template("register_form.html")


@app.route('/register', methods=["POST"])
def process_registration():
    """Process a new user's' registration form"""

    # Grab inputs from registration form
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    message = register_user(name, email, password)

    flash(message)

    return redirect("/login")


@app.route('/login', methods=["GET"])
def display_login():
    """Display login form"""

    return render_template('login_form.html')


@app.route('/login', methods=["POST"])
def log_in():
    """Log user in"""

    email = request.form.get('email')
    password = request.form.get('password')

    # Fetch user from db
    user_query = User.query.filter_by(email=email)

    # Check if user exists
    if user_query.count() == 0:
        flash("No account exists for that email")
        return redirect("/")

    user = user_query.one()

    # Check if password is correct
    if user.password == password:

        # Add user to session cookie
        session['user'] = {"id": user.user_id,
                           "name": user.name}

        return redirect("/")

    else:
        flash("Incorrect password")
        return redirect("/login")


@app.route('/logout')
def log_out():
    """Log user out"""

    # Remove user from session
    del session['user']

    return redirect("/")



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
