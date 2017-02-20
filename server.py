"""ReviewGenius"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from indexes import INDEXES
from model import Product, Review, User, connect_to_db, db
from sqlalchemy import desc
import json

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

    search_query = request.args.get('query')

    # If the search_query is more than one word, add in a &
    words = search_query.strip().split(' ')
    search_formatted = ' & '.join(words)

    # Not using search categories for now
    # search_index = request.args.get('index')

    # SQL statement to select products that match the search query
    # ranked in order of relevancy
    sql = """SELECT *, ts_rank(product_search.product_info,
                to_tsquery('english', :search_terms)) AS relevancy
             FROM (SELECT *,
                    setweight(to_tsvector('english', title), 'A') ||
                    setweight(to_tsvector('english', description), 'B') AS product_info
             FROM products) product_search
             WHERE product_search.product_info @@ to_tsquery('english', :search_terms)
             ORDER BY relevancy DESC;
          """

    cursor = db.session.execute(sql,
                                {'search_terms': search_formatted})

    # Returns a list with the top ten products
    products = cursor.fetchmany(10)


    # If there are matching products, return the listings
    if len(products) > 0:
        return render_template("product_listing.html",
                               products=products)
    else:
        return render_template("no_products.html")


@app.route('/product-reviews/<asin>.json')
def product_reviews_data(asin):
    """Return data about product reviews for chart."""

    scores = Product.query.filter_by(asin=asin).one().scores

    scores = json.loads(scores)

    score_list = [scores["1"], scores["2"], scores["3"], scores["4"], scores["5"]]

    data_dict = {
                "labels": ["1", "2", "3", "4", "5"],
                "datasets": [
                    {
                        "label": "Customer Ratings",
                        "data": score_list,
                        "backgroundColor": [
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(75, 192, 192, 0.6)',
                            'rgba(153, 102, 255, 0.6)'
                        ],
                        "hoverBackgroundColor": [
                            'rgba(255,99,132,1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)'
                        ],
                        "borderWidth": 5
                    }]
            }

    return jsonify(data_dict)


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
