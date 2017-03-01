import unittest

from server import app
from model import db, connect_to_db, example_data


class ProductGeniusTests(unittest.TestCase):
    """Tests for Product Genius."""

    def setUp(self):
        """Stuff to do before every test"""

        self.client = app.test_client()
        app.config['TESTING'] = True


    def test_homepage(self):
        """Test that homepage renders."""

        result = self.client.get("/")
        self.assertIn("Get the best information before you buy", result.data)


    def test_product_listing_page(self):
        """Test that product listing page renders."""

        pass


    def test_product_details_page(self):
        """Test that product details page renders."""

        pass


    def test_user_page(self):
        """Test that user details page renders."""

        pass


class TestUser(unittest.TestCase):
    """Tests to run when a user is logged in"""

    def setUp(self):
        """Stuff to do before every test"""

        app.config['TESTING'] = True
        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1


    def test_favorite_elements(self):
        """Test if html elements for favoriting products and
        reviews appear if user logged in
        """

        result = self.client.get("/product______")

        # Assert that review hearts are not on the page
        self.assertIn("class='heart'", result.data)

        # Assert that the product favorite button is not on the page
        self.assertIn("product-fav-button", result.data)


class TestNoUser(unittest.TestCase):
    """Tests to run when no user is logged in"""

    def setUp(self):

        app.config['TESTING'] = True
        self.client = app.test_client()


    def test_no_favorites(self):
        """Test if html elements for favoriting products and
        reviews do not appear if not logged in
        """

        result = self.client.get("/product______")

        # Assert that review hearts are not on the page
        self.assertNotIn("class='heart'", result.data)

        # Assert that the product favorite button is not on the page
        self.assertNotIn("product-fav-button", result.data)


class TestServerWithDB(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1


    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()


    def test_register(self):
        """Test whether the db updates with a new user"""

        pass


    def test_log_in(self):
        """Test messages when a user signs in incorrectly"""

        pass


    def test_search_in_reviews(self):
        """Test that ajax call to search within a review works"""

        pass


    def test_favoriting_product(self):
        """Test that favoriting a product updates the db"""

        pass


    def test_favoriting_review(self):
        """Test that favoriting a review updates the db"""

        pass


    def test_unfavoriting_product(self):
        """Test that unfavoriting a product updates the db and
           removes all favorite reviews
        """

        pass


    def test_favoriting_review_before_product(self):
        """Test that favoriting a review before the product
            favorites the product.
        """

###############################################################

if __name__ == "__main__":
    unittest.main()