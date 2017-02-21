from model import Product, connect_to_db, db
import json


def find_products(search_query, search_index):
    """Queries database to find products within a search index based on user's search.

       This full-text search in postgres stems, removes stop words, applies weights
       to different fields (title is more important than description), and ranks
       the results by relevancy.

       Currently, the default weights in ts_rank() are used, which is 1 for 'A'
       and 0.4 for 'B'. Future goal: experiment with different weightings and/or
       a cutoff for how relevant a product has to be to return.
    """

    if search_index == "All":

        sql = """SELECT *, ts_rank(product_search.product_info,
                to_tsquery('english', :search_terms)) AS relevancy
                FROM (SELECT *,
                    setweight(to_tsvector('english', title), 'A') ||
                    setweight(to_tsvector('english', description), 'B') AS product_info
                FROM products) product_search
                WHERE product_search.product_info @@ to_tsquery('english', :search_terms)
                ORDER BY relevancy DESC;
              """
    else:

        # If the search index is not "All", filter results by products within
        # the provided category
        sql = """SELECT *, ts_rank(product_search.product_info,
                to_tsquery('english', :search_terms)) AS relevancy
                FROM (SELECT *,
                    setweight(to_tsvector('english', title), 'A') ||
                    setweight(to_tsvector('english', description), 'B') AS product_info
                FROM products) product_search
                WHERE product_search.product_info @@ to_tsquery('english', :search_terms) AND
                asin IN
                    (SELECT asin
                        FROM categories
                        INNER JOIN product_categories as pc
                        USING (cat_name)
                        INNER JOIN products
                        USING (asin)
                        WHERE pc.cat_name = :category)
                ORDER BY relevancy DESC;
              """

    cursor = db.session.execute(sql,
                                {'search_terms': search_query,
                                 'category': search_index})

    # Returns a list with the top ten products
    products = cursor.fetchmany(10)

    return products


def get_scores(asin):
    """Returns the distribution of scores for a product as a list.

       ex:
        if product "P1234" had one 2-star review and four 5-star reviews,
        get_scores() would return [0, 1, 0, 0, 5]

     """

    scores = Product.query.filter_by(asin=asin).one().scores
    scores = json.loads(scores)
    score_list = (scores["1"], scores["2"], scores["3"], scores["4"], scores["5"])

    return score_list


def get_chart_data(score_list):
    """Construct data dictionary to create histogram with chart.js."""

    data_dict = {
        "labels": ["1", "2", "3", "4", "5"],
        "datasets": [{
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

    return data_dict


def find_reviews(asin, query):
    """Queries database to find product reviews based on user's search.

       This full-text search in postgres stems, removes stop words, applies weights
       to different fields (review summary is more important than the review text), 
       and ranks the results by relevancy.

       Currently, the default weights in ts_rank() are used, which is 1 for 'A'
       and 0.4 for 'B'. Future goal: experiment with different weightings and/or
       a cutoff for how relevant a review has to be to return.
    """

    sql = """SELECT *, ts_rank(review_search.review_info,
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
                                   {'search_terms': query,
                                    'asin': asin})

    reviews = cursor.fetchall()

    return reviews
