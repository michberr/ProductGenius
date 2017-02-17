# Create subsets of the product review and metadata files, based on
# the products with the most reviews

import json

def select_n_products(lst, n):
    """Select the top N products (by number of reviews)
       args:
            lst: a list of lists that are (key,value) pairs for (ASIN, N-reviews)
            sorted on the number of reviews in reverse order
            n: a list of three numbers,
       returns:
            a list of lists with N products
    """

    top_products = []

    first_third = lst[100:100 + n[0] + 1]
    second_third = lst[1000:1000 + n[1] + 1]
    third_third = lst[50000:5000 + n[2] + 1]

    top_products.extend(first_third)
    top_products.extend(second_third)
    top_products.extend(third_third)

    n_reviews = sum([x[1] for x in top_products])

    print "The number of products is: {} and the number of reviews is: {}".format(
        sum(n), n_reviews)

    return(top_products)


# Read from json file
# Output will be a dictionary where (keys, values) are (ASIN, number of reviews)
# sorted in descending order of number of reviews
with open('products-sorted-by-reviews.json') as f:
    sorted_product_reviews = json.load(f)


while True:
    # Get input from the user on the number or products to select
    # After seeing the number of products and reviews, decide to write to file
    # or try again

    first = int(raw_input("Select the number of products from 1/3: "))
    second = int(raw_input("Select the number of products from 2/3: "))
    third = int(raw_input("Select the number of products from 3/3: "))

    n_products = [first, second, third]

    products = select_n_products(sorted_product_reviews, n_products)

    response = raw_input("Is this a good amount of data? (y/n) >")

    if response == "y":

        # Create a set of all the asins
        asins = set(x[0] for x in products)

        print "============="
        print "Getting subset of products"

        # Create a subset of the product metadata
        full_metadata = open('electronics_metadata.json')
        metadata_subset = open('electronics_metadata_subset.json', 'w')

        for line in full_metadata:
            # read each line of the metadata file, if the asin is in the
            # list of products, write it to the subset file

            product = eval(line)
            if product.get('asin') in asins:
                metadata_subset.write(line)

        full_metadata.close()
        metadata_subset.close()

        print "============="
        print "Getting subset of reviews"

        # Create a subset of the reviews, based on the products selected above
        full_reviews = open('electronics_reviews.json')
        reviews_subset = open('electronics_reviews_subset.json', 'w')

        for line in full_reviews:
            review = eval(line)
            if review.get('asin') in asins:
                reviews_subset.write(line)

        full_reviews.close()
        reviews_subset.close()

        break

    else:
        continue
