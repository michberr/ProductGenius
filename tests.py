import unittest

from server import app
from model import db, connect_to_db, example_data, User, Product, Review
import json


class ProductGeniusTests(unittest.TestCase):
    """Tests for Product Genius routes that don't require db."""

    def setUp(self):
        """Stuff to do before every test"""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        """Test that homepage renders."""

        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn("Get the best information before you buy", result.data)

    def test_login_page(self):
        """Test that login page renders."""

        result = self.client.get("/login")
        self.assertEqual(result.status_code, 200)
        self.assertIn("Email", result.data)
        self.assertIn("Password", result.data)

    def test_register_page(self):
        """Test that register page renders."""

        result = self.client.get("/register")
        self.assertEqual(result.status_code, 200)
        self.assertIn("Name", result.data)
        self.assertIn("Email", result.data)
        self.assertIn("Password", result.data)


class TestDBMethods(unittest.TestCase):
    """Test basic methods for db classes.

        These tests do not require extra setup for any db objects
    """

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_register_user(self):
        """Test that registering a new user works"""

        User.register_user(name="Buddy Holly",
                           email="buddy@me.com",
                           password="abc")

        user_count = User.query.filter_by(email="buddy@me.com").count()

        self.assertEqual(user_count, 1)

    def test_calculate_score_distribution(self):
        """Test that Product.calculate_score_distribution() returns correct scores"""

        product1 = Product.query.get("A1")
        scores1 = product1.calculate_score_distribution()

        product2 = Product.query.get("A2")
        scores2 = product2.calculate_score_distribution()

        self.assertEqual(scores1, [0, 1, 0, 0, 1])
        self.assertEqual(scores2, [0, 0, 1, 0, 0])

    def test_find_products(self):
        """Test that full-text search works on products.

           In addition to finding terms in a product's
           title or description, we want to test that
           postgres is stemming and lowercasing the queries.
        """

        # Check that postgres is dealing with case
        results1 = Product.find_products('headphones')

        self.assertEqual(len(results1), 1)
        self.assertEqual(results1[0][0], "A1")

        # Check that postgres is stemming
        results2 = Product.find_products('screens')

        self.assertEqual(len(results2), 1)
        self.assertEqual(results2[0][0], "A2")

    def test_find_reviews(self):
        """Test that full-text search works on reviews.

           In addition to finding terms in a review's
           summary or body, we want to test that
           postgres is stemming and lowercasing the queries.
        """

        # Check that postgres is stemming
        results1 = Review.find_reviews('A1', 'wasted')

        self.assertEqual(len(results1), 1)
        self.assertIn("waste of money", results1[0][1])

        # Check that postgres is dealing with case
        results2 = Review.find_reviews('A2', 'trash')

        self.assertEqual(len(results2), 1)
        self.assertIn("monitor broke", results2[0][1])


class TestPGScores(unittest.TestCase):
    """Test that product genius scores are calculated correctly"""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        # Add an attribute for scores and n_scores to every product
        products = Product.query.all()

        for p in products:
            scores = p.calculate_score_distribution()
            p.scores = json.dumps(scores)
            p.n_scores = sum(scores)

            db.session.commit()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_get_total_stars(self):
        """Test that Product.get_total_stars() returns correct amount"""

        product1 = Product.query.get("A1")
        stars1 = product1.get_total_stars()

        product2 = Product.query.get("A2")
        stars2 = product2.get_total_stars()

        self.assertEqual(stars1, (7, 2))
        self.assertEqual(stars2, (3, 1))

    def test_calculate_pg(self):
        """Test that Product.calculate_pg_score() returns correct amount"""

        product1 = Product.query.get("A1")
        pg1 = product1.calculate_pg_score()

        product2 = Product.query.get("A2")
        pg2 = product2.calculate_pg_score()

        self.assertEqual(pg1, 37.0/12)
        self.assertEqual(pg2, 3.0)


class TestFavoriting(unittest.TestCase):
    """Tests methods for favoriting products and reviews"""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        # Add some favorite products and reviews for a user
        user = User.query.get(1)

        a1 = Product.query.get("A1")
        user.favorite_products.append(a1)

        review1 = Review.query.get(1)
        user.favorite_reviews.append(review1)

        db.session.commit()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_get_favorite_review_ids(self):
        """Test that User.get_favorite_review_ids() works"""

        user = User.query.get(1)
        fav_reviews = user.get_favorite_review_ids()

        self.assertEqual(len(fav_reviews), 1)
        self.assertIsInstance(fav_reviews, set)

    def test_is_favorite_product(self):
        """Test that User.is_favorite_product() works"""

        user = User.query.get(1)
        self.assertTrue(user.is_favorite_product("A1"))
        self.assertFalse(user.is_favorite_product("A2"))

    def test_is_favorite_review(self):
        """Test that User.is_favorite_review() works"""

        user = User.query.get(1)
        self.assertTrue(user.is_favorite_review(1))
        self.assertFalse(user.is_favorite_review(3))

    def test_update_favorite_product(self):
        """Test that User.update_favorite_product() works"""

        user = User.query.get(1)

        user.update_favorite_product("A1")
        user.update_favorite_product("A2")

        self.assertFalse(user.is_favorite_product("A1"))
        self.assertTrue(user.is_favorite_product("A2"))

    def test_update_favorite_review(self):
        """Test that User.update_favorite_review() works"""

        user = User.query.get(1)

        user.update_favorite_review(1)
        user.update_favorite_review(2)

        self.assertFalse(user.is_favorite_review(1))
        self.assertTrue(user.is_favorite_review(2))

    def test_add_favorite_product_from_review(self):
        """Test that User.add_favorite_product_from_review() works"""

        user = User.query.get(1)
        user.add_favorite_product_from_review("A2")

        self.assertTrue(user.is_favorite_product("A2"))

    def test_get_favorite_reviews_for_product(self):
        """Test that User.get_favorite_reviews_for_product() works"""

        user = User.query.get(1)
        fav_reviews = user.get_favorite_reviews_for_product("A1")

        self.assertEqual(len(fav_reviews), 1)

    def test_remove_favorite_reviews(self):
        """Test that User.remove_favorite_reviews() works"""

        user = User.query.get(1)
        user.remove_favorite_reviews("A1")

        self.assertFalse(user.is_favorite_review(1))


class FlaskTestNoUser(unittest.TestCase):
    """Test flask routes without a user."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        p = Product.query.get("A1")
        scores = p.calculate_score_distribution()
        p.scores = json.dumps(scores)
        p.n_scores = sum(scores)
        p.pg_score = p.calculate_pg_score()
        p.pos_words = []
        p.neg_words = []

        db.session.commit()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_product_listing_page(self):
        """Test that a product listing page loads"""

        result = self.client.get("/search?query=headphones",
                                 data={"query": "headphones"})

        self.assertIn("You searched for \"headphones\"", result.data)
        self.assertIn("Black Headphones", result.data)

    def test_product_details_page(self):
        """Test that a product details page loads"""

        result = self.client.get("/product/A1")

        # Test that product title is on page
        self.assertIn("Black Headphones", result.data)

        # Test that product genius score is on page
        self.assertIn("Product Genius Score: 3.08", result.data)

        # Test that review data is on page
        self.assertIn("These headphones had excellent sound quality", result.data)
        self.assertIn("Terrible waste of money", result.data)

    def test_register_user(self):
        """Test that registration post route works"""

        result = self.client.post("/register",
                                  data={"name": "humpty dumpty",
                                        "email": "wallsitter@yahoo.com",
                                        "password": "eggshell"},
                                  follow_redirects=True)

        # Should redirect to login and flash a message
        self.assertIn("Welcome to Product Genius", result.data)

    def test_login_user(self):
        """Test that login post route works"""

        result = self.client.post("/login",
                                  data={"email": "user@user.com",
                                        "password": "abc"},
                                  follow_redirects=True)

        # Should redirect to login and flash a message
        self.assertIn("Logged in as user", result.data)

    def test_nohearts_without_user(self):
        """Test that hearts and favorite button do not appear without login"""

        result = self.client.get("/product/A1")

        self.assertNotIn("class=\"heart\"", result.data)
        self.assertNotIn("id=\"product-fav-button\"", result.data)

    def test_navbar_without_user(self):
        """Test that navbar shows register, login when no user."""

        result = self.client.get("/")

        self.assertIn("<a href=\"/register\">Register</a>", result.data)
        self.assertIn("<a href=\"/login\">Login</a>", result.data)


class FlaskTestUser(unittest.TestCase):
    """Test flask routes with a user."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        # Set up product object
        p = Product.query.get("A1")
        scores = p.calculate_score_distribution()
        p.scores = json.dumps(scores)
        p.n_scores = sum(scores)
        p.pg_score = p.calculate_pg_score()
        p.pos_words = []
        p.neg_words = []

        db.session.commit()

        # Add some favorite products and reviews for a user
        user = User.query.get(1)
        a1 = Product.query.get("A1")
        user.favorite_products.append(a1)
        review1 = Review.query.get(1)
        user.favorite_reviews.append(review1)

        db.session.commit()

        # Add user to session
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = {"id": 1,
                                "name": "user"}

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_user_page(self):
        """Test that a user's page loads"""

        result = self.client.get("/user/1")

        self.assertIn("User: user", result.data)

        # Test user's favorite products display
        self.assertIn("www.headphones.com/headphone.jpg", result.data)

        # Test user's favorite reviews display
        self.assertIn("Great Headphones", result.data)

    def test_hearts_with_user(self):
        """Test that hearts and favorite button appear when user is logged in"""

        result = self.client.get("/product/A1")

        self.assertIn("class=\"heart\"", result.data)
        self.assertIn("id=\"product-fav-button\"", result.data)

    def test_navbar_with_user(self):
        """Test that navbar shows logout, user while user logged in."""

        result = self.client.get("/")

        self.assertIn("<a href=\"/logout\">Logout</a>", result.data)
        self.assertIn("<a href=\"/user/1\">user</a>", result.data)

    def test_search_in_reviews(self):
        """Test that ajax call to search within a review works"""

        result = self.client.get('/search-review/A1.json?query=terrible',
                                 data={"query": "terrible"},
                                 follow_redirects=True)

        # Test that reviews not matching query are not in output
        self.assertNotIn("Great Headphones", result.data)

    def test_favoriting_product(self):
        """Test that favoriting a product updates the db"""

        result = self.client.post('favorite-product',
                                  data={"asin": "A2"})
        user = User.query.get(1)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(user.is_favorite_product("A2"))

    def test_unfavoriting_product(self):
        """Test that unfavoriting a product updates the db and
           removes all favorite reviews
        """

        result = self.client.post('favorite-product',
                                  data={"asin": "A1"})
        user = User.query.get(1)

        self.assertEqual(result.status_code, 200)
        self.assertFalse(user.is_favorite_product("A1"))

    def test_favoriting_review(self):
        """Test that favoriting a review updates the db"""

        result = self.client.post('favorite-review',
                                  data={"reviewID": 2,
                                        "asin": "A1"})
        user = User.query.get(1)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(user.is_favorite_review(2))

    def test_unfavoriting_review(self):
        """Test that unfavoriting a review updates the db"""

        result = self.client.post('favorite-review',
                                  data={"reviewID": 1,
                                        "asin": "A1"})
        user = User.query.get(1)

        self.assertEqual(result.status_code, 200)
        self.assertFalse(user.is_favorite_review(1))

    def test_favoriting_review_before_product(self):
        """Test that favoriting a review before the product
            favorites the product.
        """

        result = self.client.post('favorite-review',
                                  data={"reviewID": 3,
                                        "asin": "A2"})
        user = User.query.get(1)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(user.is_favorite_review(3))
        self.assertTrue(user.is_favorite_product("A2"))



###############################################################

if __name__ == "__main__":
    unittest.main()
