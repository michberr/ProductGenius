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
        """Test that full-text search works on products"""

        results = Product.find_products('Headphones')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "A1")


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

###############################################################

if __name__ == "__main__":
    unittest.main()
