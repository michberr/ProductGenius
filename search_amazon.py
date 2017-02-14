import os
from amazon.api import AmazonAPI
from amazon_scraper import AmazonScraper
from indexes import INDEXES


AMAZON_ACCESS_KEY = os.environ['AWSAccessKeyId']
AMAZON_SECRET_KEY = os.environ['AWSSecretKey']
AMAZON_ASSOCIATE_TAG = os.environ['AWSAssociateTag']

# amazon = AmazonAPI(AMAZON_ACCESS_KEY,
#                    AMAZON_SECRET_KEY,
#                    AMAZON_ASSOCIATE_TAG)

amazon_scraper = AmazonScraper(AMAZON_ACCESS_KEY,
                               AMAZON_SECRET_KEY,
                               AMAZON_ASSOCIATE_TAG)


def get_amazon_results(query, index='All'):
    """Get amazon search results based on a user query.

    Args:
        query: user search query
        index: which index to search from. Default index is 'All',
        but user can specify an index from a dropdown menu.

    Returns:
        an Item that contains ASIN, and item attributes

       Note to self:
       Need to look further into rate limits to decide whether to user
       search() or search_n()
    """

    products = amazon.search_n(10, Keywords=query, SearchIndex=index)

    items = []

    for product in products:
        items.append(product.Item)

    return items



# def get_product_reviews():
#     """ """

#     return "not working"


# def get_product_ratings():
#     """ """

#     return "not working"


if __name__ == "__main__":

    # For debugging purposes:
    print "====== KEYS ======"
    print AMAZON_ACCESS_KEY
    print AMAZON_SECRET_KEY
    print AMAZON_ASSOCIATE_TAG

    products = amazon.search(Keywords='kindle', SearchIndex='All')

    print "Length of products is {}".format(len(products))
