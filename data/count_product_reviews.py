# File to create subsets from the amazon review data

import operator
import json

# Dictionary to hold ASIN, n-values
product_reviews = {}

review_file = open('electronics_reviews.json')

# create dictionary from reviews file
for line in review_file:
    review = eval(line)
    product_id = review["asin"]
    product_reviews[product_id] = product_reviews.get(product_id, 0) + 1

review_file.close()

# Create tuples of (key,value) pairs and sort based on the value
sorted_product_reviews = sorted(product_reviews.items(),
                                key=operator.itemgetter(1),
                                reverse=True)

# Save to file
with open('products-sorted-by-reviews.json', 'w') as f:
    json.dump(sorted_product_reviews, f)
