## Makes calls to Amazon product advertising API and seeds database
## with product information

from model import connect_to_db, db
from model import Product, Review
from search_amazon import amazon, get_amazon_results
from server import app
from faker import Faker
from random import choice, randint, sample

##################### Seed Products ###########################

PRODUCTS = ["milk frother", "umbrella", "earbuds", "electric kettle",
            "python programming book", "keyboard", "tent", "ruby on rails",
            "laptop case", "iphone case"]

def load_products():
    """Load products and their reviews into database."""

    for product in PRODUCTS:

        print "Loading data for {}".format(product)

        results = get_amazon_results(product)

        product = Product(asin=,
                          title=,
                          price=,
                          author=,
                          url=,
                          image=results)

        db.session.add(product)
        db.session.commit()

        # Get reviews and add them to the database
        reviews = get_reviews_from_asin(asin)

        for review in reviews:
            review = Review(review_id=,
                            review=,
                            asin=asin)

            db.session.add(review)

        db.session.commit()


##################### Seed Users ###############################

N_USERS = 10

def load_users():
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

    # Create User favorite products and reviews

    # Select a random number of products for the user to have
    n_products = randint(0, len(PRODUCTS)-1)
    user_products = sample(PRODUCTS, n_products)

    for product in user_products:

        asin = Product.query.filter_by()
        favorite_product = FavoriteProduct()




##################### Run script #################################

if __name__ == "__main__":

    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Delete rows from table, so we don't replicate rows if this script is rerun
    Product.query.delete()
    Review.query.delete()

    load_products()
    load_users()
