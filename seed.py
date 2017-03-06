## seeds database with product information
## and fake user data

from model import connect_to_db, db
from model import Product, Review, User, Category
from server import app
from faker import Faker
from random import randint, sample
from datetime import datetime
import json
from HTMLParser import HTMLParser
from keyword_extraction import get_keywords_from_naive_bayes


##################### Seed Products ###########################

def load_products(filename):
    """Load products from json-like file into database."""

    print "=================="
    print "loading products"

    f = open(filename)

    for line in f:
        # Each line is a dictionary containing info on a product
        p = eval(line)

        # categories are stored in double brackets for weird semi-json reasons
        categories = p['categories'][0]

        for c in categories:
            # Loop through each of the product's categories, add to the
            # categories table if it's not there

            n_results = Category.query.filter_by(cat_name=c).count()

            if n_results == 0:
                category = Category(cat_name=c)
                db.session.add(category)
                db.session.commit()

        # Pull out the product's categories again as a list of Category objects
        category_objects = Category.query.filter(Category.cat_name.in_(categories)).all()

        title = p.get('title')
        if title:
            title = H.unescape(title)

        description = p.get('description')
        if description:
            description = H.unescape(description)

        # Instantiate a product object
        product = Product(asin=p['asin'],
                          title=title,
                          description=description,
                          price=p.get('price'),
                          image=p.get('imUrl'),
                          categories=category_objects)

        db.session.add(product)
        db.session.commit()



##################### Seed Reviews ###########################

def load_reviews(filename):
    """Load reviews from json-like file into database."""

    print "=================="
    print "loading reviews"

    f = open(filename)

    for line in f:
        # Each line is a review for one product in the products table
        r = eval(line)

        review_time = datetime.strptime(r['reviewTime'], '%m %d, %Y')

        summary = H.unescape(r['summary'])
        review = H.unescape(r['reviewText'])

        # Create a new review object and add it to the reviews table
        review = Review(review=r['reviewText'],
                        asin=r['asin'],
                        score=r['overall'],
                        summary=summary,
                        time=review_time)

        db.session.add(review)

    db.session.commit()


def create_search_indexes():
    """Create a prostgres search index on products and reviews """

    print "====================="
    print "Creating search indexes"

    pr_index = """CREATE INDEX idx_fts_product ON products
                  USING gin((setweight(to_tsvector('english', title), 'A') ||
                  setweight(to_tsvector('english', description), 'B')));
               """

    rev_index = """CREATE INDEX idx_fts_review ON reviews
                   USING gin((setweight(to_tsvector('english', summary), 'A') ||
                   setweight(to_tsvector('english', review), 'B')));
                """

    db.session.execute(pr_index)
    db.session.execute(rev_index)

    db.session.commit()


def count_scores():
    """Calculate score distribution, pg-score and update product object in db """

    print "======================"
    print "calculating review distributions"

    for product in Product.query.all():

        # Loop through all products. Calculate the distribution of reviews
        # and add to the database as a json. Also add the number of reviews
        score_distribution = product.calculate_score_distribution()
        product.scores = json.dumps(score_distribution)
        product.n_scores = sum(score_distribution)
        product.pg_score = product.calculate_pg_score()

        db.session.commit()


def extract_product_keywords_from_reviews():
    """Extract the top ten positive and negative keywords from reviews"""

    print "======================"
    print "extracting keywords"

    for product in Product.query.all():

        # Loop through all products. Run naive bayes to extract the 10
        # keywords with the highest likelihood of being in positive
        # and negative reviews

        # Include the product's name as stop words
        more_stop_words = product.title.split(' ')
        more_stop_words = [w.lower() for w in more_stop_words]

        # keywords is a tuple with a list of positive keywords and negative keywords
        keywords = get_keywords_from_naive_bayes(product, more_stop_words)

        # need to do tuple unpacking
        product.pos_words = keywords[0]
        product.neg_words = keywords[1]

        db.session.commit()


##################### Seed User data ###############################

N_USERS = 10


def create_users():
    """Creates fake users and loads them into the db"""

    print "====================="
    print "Creating fake users"

    # Instantiate a Faker object
    fake = Faker()
    fake.seed(435)

    # Create N user objects and add them to the db
    for i in range(N_USERS):

        user = User(name=fake.name(),
                    email=fake.email(),
                    password=fake.bs())

        db.session.add(user)

    db.session.commit()


def create_favorite_products():
    """Create User favorite products"""

    users = User.query.all()
    products = Product.query.all()

    for user in users:

        # Select a random number of products for the user to have from 0-15
        n_products = randint(0, 15)
        user_products = sample(products, n_products)

        for product in user_products:

            user.favorite_products.append(product)

    db.session.commit()



##################### Run script #################################

if __name__ == "__main__":

    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    H = HTMLParser()

    load_products('data/electronics_metadata_subset.json')
    load_reviews('data/electronics_reviews_subset.json')
    count_scores()
    extract_product_keywords_from_reviews()
    create_search_indexes()
    create_users()
    create_favorite_products()
