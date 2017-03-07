from flask_sqlalchemy import SQLAlchemy
import json
import numpy as np

db = SQLAlchemy()


class User(db.Model):
    """User object"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    favorite_products = db.relationship('Product',
                                        secondary='favorite_products',
                                        lazy='dynamic')

    favorite_reviews = db.relationship('Review',
                                       secondary='favorite_reviews',
                                       lazy="dynamic")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        """Display when printing a User object"""

        return "<User: {} email: {}>".format(self.user_id, self.email)

    def get_favorite_review_ids(self):
        """Return a set of a user's favorite review id's """

        return set(rev.review_id for rev in self.favorite_reviews)

    def is_favorite_product(self, asin):
        """Return a boolean for whether a product is a user's favorite"""

        favorite = self.favorite_products.filter_by(asin=asin)

        return favorite.count() != 0

    def is_favorite_review(self, review_id):
        """Return a boolean for whether a review is a user's favorite"""

        favorite = self.favorite_reviews.filter_by(review_id=review_id)

        return favorite.count() != 0

    def update_favorite_product(self, asin):
        """Update a product's favorited-status in a user's account"""

        product = Product.query.get(asin)

        if self.is_favorite_product(asin):

            # If the user has favorited the item, remove the favorite from the db
            self.favorite_products.remove(product)
            db.session.commit()
            return "Unfavorited"

        else:

            # If the user has not favorited the product, add it to the db
            self.favorite_products.append(product)
            db.session.commit()
            return "Favorited"

    def update_favorite_review(self, review_id):
        """Update a review's favorited-status in a user's account"""

        rev = Review.query.get(review_id)

        if self.is_favorite_review(review_id):

            # If the user has favorited the item, remove the favorite from the db
            self.favorite_reviews.remove(rev)
            db.session.commit()
            return "Unfavorited"

        else:

            # If the user has not favorited the review, add it to the db
            self.favorite_reviews.append(rev)
            db.session.commit()
            return "Favorited"

    def add_favorite_product_from_review(self, asin):
        """Verify that a product is favorited.

           This function is called when a user favorites a review. If they
           haven't already favorited a product, it should automatically favorite
           the product.
        """

        if not self.is_favorite_product(asin):
            product = Product.query.get(asin)
            self.favorite_products.append(product)
            db.session.commit()

    def get_favorite_reviews_for_product(self, asin):
        """Return a list of review objects that a user favorited for a given product"""

        return self.favorite_reviews.filter_by(asin=asin).all()

    def remove_favorite_reviews(self, asin):
        """Removes all favorited reviews for a product.

           This function is called when a user unfavorites a product.
        """

        # Query a user's favorite reviews for that product
        product_fav_reviews = self.get_favorite_reviews_for_product(asin)

        for review in product_fav_reviews:
            self.favorite_reviews.remove(review)

        db.session.commit()

    @classmethod
    def register_user(cls, name, email, password):
        """Register a new user"""

        user = cls(name=name,
                   email=email,
                   password=password)

        # Add user to the session
        db.session.add(user)

        # Commit transaction to db
        db.session.commit()


class Product(db.Model):
    """Product object"""

    __tablename__ = "products"

    asin = db.Column(db.Text, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.Text, nullable=False)   # link to image
    scores = db.Column(db.JSON)                  # List with 1-5 star ratings stored as json
    n_scores = db.Column(db.Integer)
    pg_score = db.Column(db.Float)             # Product Genius score
    pos_words = db.Column(db.JSON)               # List of positive keywords stored as json
    neg_words = db.Column(db.JSON)               # List of negative keywords stored as json

    categories = db.relationship('Category',
                                 secondary='product_categories',
                                 back_populates='products')

    reviews = db.relationship('Review',
                              order_by='Review.time',
                              back_populates='product')

    def __init__(self, asin, title, description, price, image, categories):
        self.asin = asin
        self.title = title
        self.description = description
        self.price = price
        self.image = image
        self.categories = categories
        self.pos_words = []
        self.neg_words = []

    def __repr__(self):
        """Display when printing a Product object"""

        return "<Product: {} name: {}>".format(self.asin, self.title)

    def calculate_score_distribution(self):
        """Calculates the distribution of 1,2,3,4,5 star reviews"""

        distribution = [0, 0, 0, 0, 0]

        for review in self.reviews:
            distribution[review.score - 1] += 1

        return distribution

    def get_scores(self):
        """Return the distribution of scores for a product as a list.

           ex:
            if product "P1234" had one 2-star review and four 5-star reviews,
            get_scores() would return [0, 1, 0, 0, 5]
         """

        return json.loads(self.scores)

    def get_total_stars(self):
        """Return a product's total stars and n reviews as a tuple"""

        scores = self.get_scores()

        stars = sum(np.array(scores) * np.array([1, 2, 3, 4, 5]))

        # Return a tuple with (nstars, nscores)
        return (stars, self.n_scores)

    def calculate_pg_score(self, pg_average=3.0, C=10):
        """Calculate Product Genius score with bayesian average"""

        stars, n_scores = self.get_total_stars()
        pg_score = (C * pg_average + stars)/(C + n_scores)

        return pg_score

    @classmethod
    def get_mean_product_score(cls):
        """Calculate mean product score across all products."""

        products = cls.query.all()

        # List of product (star, nscores) tuples
        star_tups = [pr.get_total_stars() for pr in products]

        product_average = float(sum([tup[0] for tup in star_tups]))/sum([tup[1] for tup in star_tups])

        return product_average

    @staticmethod
    def find_products(query):
        """Queries database to find products based on user's search.

           This full-text search in postgres stems, removes stop words, applies weights
           to different fields (title is more important than description), and ranks
           the results by relevancy.

           Currently, the default weights in ts_rank() are used, which is 1 for 'A'
           and 0.4 for 'B'. Future goal: experiment with different weightings and/or
           a cutoff for how relevant a product has to be to return.
        """

        # If the search_query is more than one word,
        # need to format the query for sql with a '&' in between words
        words = query.strip().split(' ')
        search_formatted = ' & '.join(words)

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

        # Returns a list of product tuples
        return cursor.fetchall()


class Review(db.Model):
    """Review object"""

    __tablename__ = "reviews"

    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    review = db.Column(db.Text, nullable=False)
    asin = db.Column(db.Text, db.ForeignKey('products.asin'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    # Define relationship to product
    product = db.relationship('Product',
                              back_populates='reviews')

    def __init__(self, review, summary, asin, score, time):
        self.review = review
        self.summary = summary
        self.asin = asin
        self.score = score
        self.time = time

    def __repr__(self):
        """Display when printing a Review object"""

        return "<Review: {} asin: {} summary: {}>".format(self.review_id,
                                                          self.asin,
                                                          self.summary)

    @staticmethod
    def find_reviews(asin, query):
        """Queries database to find product reviews based on user's search.

           This full-text search in postgres stems, removes stop words, applies weights
           to different fields (review summary is more important than the review text),
           and ranks the results by relevancy.

           Currently, the default weights in ts_rank() are used, which is 1 for 'A'
           and 0.4 for 'B'. Future goal: experiment with different weightings and/or
           a cutoff for how relevant a review has to be to return.
        """

        # If the search_query is more than one word,
        # need to format the query for sql with a '&' in between words
        words = query.strip().split(' ')
        search_formatted = ' & '.join(words)

        sql = """SELECT *, ts_rank(array[0, 0, 0.8, 1], review_search.review_info,
                    to_tsquery('english', :search_terms)) AS relevancy
                    FROM (SELECT *,
                        setweight(to_tsvector('english', summary), 'A') ||
                        setweight(to_tsvector('english', review), 'B') AS review_info
                    FROM reviews
                    WHERE asin=:asin) review_search
                    WHERE review_search.review_info @@ to_tsquery('english', :search_terms)
                    ORDER BY relevancy DESC;
              """

        cursor = db.session.execute(sql,
                                    {'search_terms': search_formatted,
                                     'asin': asin})
        return cursor.fetchall()


class Category(db.Model):
    """Product categories"""

    __tablename__ = "categories"

    cat_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    cat_name = db.Column(db.Text)

    products = db.relationship('Product',
                               secondary='product_categories',
                               back_populates='categories')

    def __init__(self, cat_name):
        self.cat_name = cat_name

    def __repr__(self):
        """Display when printing a Category object"""

        return "<Category: {}>".format(self.cat_name)


# Crosslink between products and categories
product_categories = db.Table('product_categories',
    db.Column('asin', db.Text, db.ForeignKey('products.asin'), primary_key=True),
    db.Column('cat_id', db.Integer, db.ForeignKey('categories.cat_id'), primary_key=True)
)

# Crosslink between users and favorited products
favorite_products = db.Table('favorite_products',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('asin', db.Text, db.ForeignKey('products.asin'), primary_key=True)
)

# Crosslink between users and favorited reviews
favorite_reviews = db.Table('favorite_reviews',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('review_id', db.Integer, db.ForeignKey('reviews.review_id'), primary_key=True)
)


##############################################################################
# Helper functions

def connect_to_db(app, db_uri="postgresql:///product_genius"):
    """Connect the database to Flask app."""

    # Configure to use PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)

def example_data():
    """Create example data for the test database."""

    product1 = Product(asin='A1',
                       title='Black Headphones',
                       description="Black Headphones",
                       price=100,
                       image="www.headphones.com/headphone.jpg",
                       categories=[])

    review1 = Review(review='These headphones had excellent sound quality',
                     asin='A1',
                     score=5,
                     summary="Great Headphones",
                     time="2016-02-12 00:00:00")

    review2 = Review(review='Terrible waste of money',
                     asin='A1',
                     score=2,
                     summary="Poor quality",
                     time="2014-05-03 17:45:35")

    product2 = Product(asin='A2',
                       title='Monitor',
                       description="Monitor screen",
                       price=400,
                       image="www.monitors.com/monitor.jpg",
                       categories=[])

    review3 = Review(review='This monitor broke after a week',
                     asin='A2',
                     score=3,
                     summary="Trash",
                     time="2011-05-03 17:45:35")

    user = User(name='user',
                email="user@user.com",
                password="abc")

    db.session.add_all([product1, review1, review2, product2, review3, user])
    db.session.commit()


if __name__ == "__main__":
    # Work with database directly if run interactively

    from server import app
    connect_to_db(app)
    print "Connected to DB."
