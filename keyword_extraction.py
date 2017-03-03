# Script that uses naive bayes to identify
# which words are most likely to be associated
# with positive or negative reviews for a product

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support


def get_keywords_from_naive_bayes(product):
    """Extracts positive/negative words from a product's reviews with Naive Bayes

    Input is a product object.
    Output is a dictionary with (keyword, label) as (k, v).
    Label is either "positive" or "negative" depending on the score the reviewer
    gave the product. A positive review gave the product 4 or 5 stars. A negative
    review gavethe product 1 or 2 stars.
    """

    # list of labels for a review: positive or negative
    labels = []

    # list of reviews
    reviews = []

    for rev in product.reviews:
        # Iterate through a products reviews,
        # If the score is a 1 or 2, label it as negative
        # If the score is a 4 or 5, label it as positive
        # This algorithm throws out reviews with a score of 3

        if rev.score < 3:
            labels.append("negative")
            reviews.append(rev.review)

        elif rev.score > 3:
            labels.append("positive")
            reviews.append(rev.review)

    # Instantiate a Text-frequency, inverse document frequency vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')

    # Convert our list of reviews into a sparse matrix of word counts where the
    # rows are reviews and the columns are words
    X = vectorizer.fit_transform(reviews)
    y = np.array(labels)

    # Fit model
    nb = MultinomialNB()
    nb.fit(X, y)

    # probabilities for most negative words
    pos_probs = nb.feature_log_prob_[1] - nb.feature_log_prob_[0]

    # probabilities for most positive words
    neg_probs = nb.feature_log_prob_[0] - nb.feature_log_prob_[1]

    # array of words
    features = vectorizer.get_feature_names()

    # list of (probability, word) tuples sorted by log probabilities in descending order
    pos_probs_and_words = sorted(zip(pos_probs, features), reverse=True)[:10]
    neg_probs_and_words = sorted(zip(neg_probs, features), reverse=True)[:10]

    pos_words = [tup[1] for tup in pos_probs_and_words]
    neg_words = [tup[1] for tup in neg_probs_and_words]

    # returns a tuple of positive and negative keywords
    return (pos_words, neg_words)


def cross_validation(nb, X, y):
    """Run cross validation on a naive bayes review classifier"""

    # Do cross-validation with 5 folds
    # Stratified kfolds is useful when you have class imbalance to make sure you
    # have elements of both classes in each training set
    skf = StratifiedKFold(n_splits=5)

    # variable to store the cumulartive confusion matrix of all kfolds
    cm = np.zeros((2, 2))

    precision = []
    recall = []

    for train, test in skf.split(X, y):
        # Split X and y into training and test set
        X_train, X_test, y_train, y_test = X[train], X[test], y[train], y[test]

        # Fit the model with the training data
        nb.fit(X_train, y_train)

        # Predict on the test-set
        y_hat = nb.predict(X_test)

        # Calculate the confusion matrix of this fold, and add it to cm
        cm += confusion_matrix(y_test, y_hat, labels=['positive', 'negative'])

        # Calculate precision and recall
        p, r, fscore, support = precision_recall_fscore_support(y_test, y_hat)
        if len(p) > 1:
            precision.append(p[1])
            recall.append(r[1])

    return (precision, recall)


# if __name__ == "__main__":

    # Run cross validation on 100 of the products and average the data
