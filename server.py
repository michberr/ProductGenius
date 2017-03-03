"""ReviewGenius"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from product_indexes import INDEXES
from model import User, Product, Review, connect_to_db, db
from product_genius import get_chart_data, format_reviews_to_dicts
# import sqlalchemy

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
    products = Product.find_products(search_query, search_index)

    print len(products[0])

    if len(products) > 0:
        return render_template("product_listing.html",
                               query=search_query,
                               products=products)
    else:
        return render_template("no_products.html")


@app.route('/product-scores/<asin>.json')
def product_reviews_data(asin):
    """Return data about product reviews for histogram."""

    product = Product.query.get(asin)
    score_list = product.get_scores()

    # Formatting for a chart.js object
    data_dict = get_chart_data(score_list)

    return jsonify(data_dict)


@app.route('/search-review/<asin>.json')
def search_reviews(asin):
    """Perform full-text search within product reviews.
       Returns the matching reviews via json to the front end.
    """

    search_query = request.args.get('query')

    # Run full-text search within a product's reviews
    # Return a list of review tuples.
    reviews = Review.find_reviews(asin, search_query)

    user_id = None

    if "user" in session:
        user_id = session["user"]["id"]

    # Converts list of review tuples into a list of dictionaries
    review_dict_list = format_reviews_to_dicts(reviews, user_id)

    return jsonify(review_dict_list)


@app.route('/product/<asin>')
def display_product_profile(asin):
    """Display a product details page.

       Should have a pretty histogram with scores, a product rating
       built from bayesian logic, the product's reviews, a search bar for
       reviews (that returns w/ ajax), and a heart to favorite the product.
    """

    product = Product.query.get(asin)

    favorite_reviews = None
    is_favorite = None

    if "user" in session:
        user_id = session["user"]["id"]
        user = User.query.get(user_id)

        # Return a set of their favorite reviews, and a boolean for whether
        # they favorited the product on this page
        favorite_reviews = user.get_favorite_review_ids()
        is_favorite = user.is_favorite_product(asin)

    return render_template("product_details.html",
                           product=product,
                           is_favorite=is_favorite,
                           favorite_reviews=favorite_reviews)


##################### Favorites ################################

@app.route('/user/<user_id>')
def display_user_profile(user_id):
    """Display user's favorite products and reviews.

       User should be able to compare products/reviews side by side.
       Might add functionality to add to the amazon cart via their API
    """

    user_id = int(user_id)
    user = User.query.get(user_id)

    for pr in user.favorite_products:

        # Attach an attribute list to the product, with the user's favorited reviews
        pr.favorited_reviews = pr.get_users_favorite_reviews(user_id)

    return render_template("user_page.html",
                           user=user,
                           favorite_products=user.favorite_products)


@app.route('/favorite-product', methods=['POST'])
def favorite_product():
    """Adds or removes a product from a user's favorites.

       Returns a message of whether the product was favorited or unfavorited.
    """

    asin = request.form.get('asin')
    user_id = session['user']['id']

    user = User.query.get(user_id)

    # Adds or removes a product from a user's favorites
    favorite_status = user.update_favorite_product(asin)

    # If the user unfavorites a product, remove all favorited reviews
    if favorite_status == "Unfavorited":
        user.remove_favorite_reviews(asin)

    return favorite_status


@app.route('/favorite-review', methods=['POST'])
def favorite_review():
    """Add or remove a product review from a user's favorites

       Returns a message of whether the review was favorited or unfavorited
    """

    review_id = request.form.get('reviewID')
    asin = request.form.get('asin')
    user_id = session['user']['id']

    user = User.query.get(user_id)

    # Adds or removes a product from a user's favorites
    favorite_status = user.update_favorite_review(review_id)

    # If the user favorites a review, automatically favorite the product
    if favorite_status == "Favorited":
        user.add_favorite_product_from_review(asin)

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

    if User.query.filter_by(email=email).count() != 0:
        message = "That email already exists. Please login or register for a new account"
    else:
        User.register_user(name, email, password)
        message = "Welcome to ProductGenius"

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

        flash("Logged in as {}".format(user.name))
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
