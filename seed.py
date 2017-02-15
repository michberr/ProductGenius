## seeds database with product information
## and fake user data

from model import connect_to_db, db
from model import Product, Review, User, FavoriteProduct
from server import app
from faker import Faker
from random import randint, sample
from datetime import datetime


##################### Seed Products ###########################

def load_products(filename):
    """Load products from json-like file into database."""

    print "=================="
    print "loading products"

    f = open(filename)
    for line in f:
        product = eval(line)

        product = Product(asin=product['asin'],
                          title=product['title'],
                          price=product.get('price'),
                          author=product.get('author'),
                          image=product.get('imUrl'))

        db.session.add(product)
    db.session.commit()


def load_reviews(filename):
    """Load reviews from json-like dile into database."""

    print "=================="
    print "loading reviews"

    f = open(filename)
    for line in f:
        review = eval(line)

        total_votes = review['helpful'][1]
        helpful_votes = review['helpful'][0]

        if total_votes != 0:
            helpful_fraction = helpful_votes/total_votes
        else:
            helpful_fraction = 0

        # review_time = datetime.strptime(review['reviewTime'], '%m %e, %Y')

        new_review = Review(reviewer_id=review['reviewerID'],
                            reviewer_name=review.get('reviewer_name'),
                            review=review['reviewText'],
                            asin=review['asin'],
                            helpful_total=total_votes,
                            helpful_fraction=helpful_fraction,
                            rating=review['overall'],
                            summary=review['summary'][:-2]) # Strip off trailing chars
                            # time=review_time)

        db.session.add(new_review)

    db.session.commit()


##################### Seed Users ###############################

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

            favorite_product = FavoriteProduct(asin=product.asin,
                                               user_id=user.user_id)
            db.session.add(favorite_product)

    db.session.commit()




##################### Run script #################################

if __name__ == "__main__":

    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Delete rows from table, so we don't replicate rows if this script is rerun
    FavoriteProduct.query.delete()
    User.query.delete()
    Product.query.delete()
    Review.query.delete()

    load_products('data/electronics_metadata_subset_clean.json')
    load_reviews('data/electronics_reviews_subset.json')
    create_users()
    create_favorite_products()
