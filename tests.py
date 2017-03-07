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


###############################################################

if __name__ == "__main__":
    unittest.main()
