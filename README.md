#Product Genius

Product Genius enables consumers to make data-driven decisions about products. Most online shopping sites display a product's average rating, which can be misleading for products with few reviews. Product Genius implements its own rating system, using Bayesian averaging, to present a more robust metric to the consumer. Product Genius also aggregates useful information from customer reviews, using machine learning to extract the most relevant terms from positive and negative reviews of a product. Finally, users can search within a product's reviews and favorite the most relevant ones, to assist with side-by-side product comparisons.

##Technology Stack

**Frontend:** HTML, CSS, Javascript, jQuery, jQcloud, Chart.js, Bootstrap, Jinja<br/>
**Backend:** Python, Flask, PostgreSQL, SQLAlchemy, NumPy, Scikit-Learn<br/>

Product Genius has 74% test coverage - see `tests.py`

![image](/static/img/homepage.png)

##Search for Products

Users can search for products on the homepage or from the navbar. When the user clicks <kbd>Search</kbd>, the input from the form is passed to the postgres database. The database performs an intelligent and efficient search, handling case, stemming the query, and returning the most relevant products. Relevancy
is determined by ranking matches to the product title above matches to the product description. The entire search is performed efficiently with a GIN index.
You can read more about full-text search in postgres [here](http://rachbelaid.com/postgres-full-text-search-is-good-enough/).

![image](/static/img/search_results.png)

##Product Genius scores using Bayesian Averaging

Users can view the Product Genius score on the product details page. Most websites report a product's average review score - this is a poor metric when a product only has a few reviews! Two five-star ratings are not the same as 500. Product Genius understands this and uses Bayesian logic to provide a score that better represents customer satisfaction. The Product Genius score is a weighted average of a product's actual reviews and a prior expectation that unreviewed products would be on average a "3". Read more about Bayesian Averages [here](https://en.wikipedia.org/wiki/Bayesian_average)

![image](/static/img/pg_score.png)

##Extracting Review Keywords with Naive Bayes

Rather than reading lengthy product descriptions, specs and reviews, users can quickly get a summary of the good and bad about a product by looking at the review keywords. These clouds were populated with a Naive Bayes model built with scikit-learn. Reviews were considered positive if they rated a product a 4 or 5, and negative if they rated a product a 1 or a 2. After the classifier was trained to predict positive and negative reviews, the 10 words with the highest likelihoods of being in either class were extracted. The model was cross-validated using KFolds on a sample of 50 products, yielding over 90% precision and recall. The model code can be found in `keyword_extraction.py`.

![image](/static/img/keywords.png)

##Advanced review search

Scanning through hundreds of product reviews is time consuming! Product Genius allows users to search directly within product reviews for the terms they care about. Like the product search, the advanced review search handles case, stemming, and ranks results by relevancy. Reviews are considered more relevant if the term appears in the title than the body of the review. The search call is made via AJAX, and a jquery highlight plugin was used to highlight the user's search query in the results. 

![image](/static/img/review_search.png)


##Favoriting Products and Reviews

To use this feature, users must create an account or sign in prior to searching. 

![image](/static/img/login.png)


When the user clicks on <kbd>Favorite</kbd> next to a product, or the heart next to a review, that information is stored in the database. If a user favorites a review, the product is automatically favorited. If a user unfavorites a product, all of their favorited reviews are removed as well. 

![image](/static/img/favorite.png)

A user can view their favorite products and reviews by visiting their profile page. 

![image](/static/img/user_page.png)


##Set up

Clone or fork this repo:

```
https://github.com/mich_berr/ProductGenius.git
```

Create and activate a virtual environment inside your project directory:

```
virtualenv env
source env/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```


Set up the database:

```
psql product_genius < product_genius.sql
```
** The code and data that seeded the original database can be found in 
`seed.py` and `/data`

Run the app:

```
python server.py
```

Navigate to `localhost:5000/` to begin researching products!

##Future Plans
Features I plan to implement in the future include testing for bimodal product rating distributions, additional sorting and filtering features for products, and improvements to the existing keyword extraction model using stemming and corrections for class imbalance.
     

##The Author

Product Genius was created by Michelle Berry, a software engineer and data scientist in San Francisco. Michelle completed the Software Engineering Fellowship at Hackbright Academy and holds graduate and undergraduate degrees in Earth Systems and Human Biology from Stanford University.

Learn more about Michelle at her [LinkedIn](https://www.linkedin.com/in/michelle-ariela-berry).

