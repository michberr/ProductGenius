# File to create subsets from the amazon review data


# metadata subset was created using bash's 'head'
# We read through each line and store the asin in a set
products = set()
metadata_file = open('electronics_metadata_subset.json')
metadata_with_title = open('electronics_metadata_subset_clean.json', 'w')

for line in metadata_file:
    product = eval(line)
    if product.get('title'):
        products.add(product['asin'])
        metadata_with_title.write(line)

metadata_file.close()
metadata_with_title.close()

# Now, we open the reviews file and new file to write the subset to
# We iterate through each line of the reviews file and only add to
# the write file if the asin is in the products set.

review_subset = open('electronics_reviews_subset.json', 'w')
review_file = open('reviews_Electronics_5.json')

for line in review_file:
    review = eval(line)
    if review["asin"] in products:
        review_subset.write(line)

review_subset.close()
